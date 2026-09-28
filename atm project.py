import mysql.connector
import random
import time
from datetime import datetime


# =====================================================
# DATABASE CONNECTION
# =====================================================

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1214",
        database="atm"
    )


# =====================================================
# LANGUAGE
# =====================================================

language = "English"


def t(english, hindi):
    if language == "Hindi":
        return hindi
    return english


# =====================================================
# CLEAR SCREEN
# =====================================================

def clear_screen():
    print("\n" * 35)


def pause():
    input("\n" + t(
        "Press Enter to continue...",
        "आगे जाने के लिए Enter दबाएं..."
    ))


# =====================================================
# LANGUAGE SELECTION
# =====================================================

def select_language():

    global language

    clear_screen()

    print("======================================")
    print("          WELCOME TO ATM")
    print("       ATM में आपका स्वागत है")
    print("======================================")

    print("\n1. English")
    print("2. हिंदी")

    choice = input("\nSelect Language / भाषा चुनें: ")

    if choice == "2":
        language = "Hindi"
    else:
        language = "English"


# =====================================================
# GENERATE CARD NUMBER
# =====================================================

def generate_card_number():

    while True:

        card_number = "6222" + "".join(
            str(random.randint(0, 9))
            for _ in range(12)
        )

        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "SELECT id FROM users WHERE card_number=%s",
            (card_number,)
        )

        result = cur.fetchone()

        cur.close()
        con.close()

        if result is None:
            return card_number


# =====================================================
# CREATE NEW ACCOUNT
# =====================================================

def create_account():

    clear_screen()

    print("======================================")
    print(t(
        "CREATE NEW ACCOUNT",
        "नया अकाउंट बनाएं"
    ))
    print("======================================")

    name = input(
        t(
            "Enter your name: ",
            "अपना नाम डालें: "
        )
    )

    mobile = input(
        t(
            "Enter mobile number: ",
            "मोबाइल नंबर डालें: "
        )
    )

    while True:

        try:

            deposit_amount = float(
                input(
                    t(
                        "Enter initial deposit: ₹",
                        "प्रारंभिक जमा राशि डालें: ₹"
                    )
                )
            )

            if deposit_amount < 0:
                print(t(
                    "Invalid amount.",
                    "गलत राशि।"
                ))
                continue

            break

        except ValueError:

            print(t(
                "Please enter a valid amount.",
                "कृपया सही राशि डालें।"
            ))

    con = connect_db()
    cur = con.cursor()

    # New account number
    cur.execute("SELECT MAX(id) FROM users")

    result = cur.fetchone()

    if result[0] is None:
        account_number = 101
    else:
        account_number = int(result[0]) + 1

    card_number = generate_card_number()

    # PIN initially not set
    query = """
        INSERT INTO users
        (
            id,
            name,
            password,
            balance,
            card_number,
            mobile,
            pin_set,
            failed_attempts,
            status
        )
        VALUES
        (%s, %s, NULL, %s, %s, %s, 0, 0, 'ACTIVE')
    """

    cur.execute(
        query,
        (
            account_number,
            name,
            deposit_amount,
            card_number,
            mobile
        )
    )

    con.commit()

    cur.close()
    con.close()

    record_transaction(
        account_number,
        "ACCOUNT_OPEN",
        deposit_amount,
        deposit_amount
    )

    print("\n======================================")
    print(t(
        "ACCOUNT CREATED SUCCESSFULLY",
        "अकाउंट सफलतापूर्वक बन गया"
    ))
    print("======================================")

    print(
        t(
            f"Account Number : {account_number}",
            f"अकाउंट नंबर : {account_number}"
        )
    )

    print(
        t(
            f"Card Number    : {card_number}",
            f"कार्ड नंबर : {card_number}"
        )
    )

    print(
        t(
            "PIN is not set yet.",
            "PIN अभी सेट नहीं है।"
        )
    )

    print(
        t(
            "Please insert this card and set your PIN.",
            "इस कार्ड को डालकर अपना PIN सेट करें।"
        )
    )

    pause()


# =====================================================
# CARD INSERT
# =====================================================

def insert_card():

    clear_screen()

    print("======================================")
    print(
        t(
            "PLEASE INSERT YOUR ATM CARD",
            "कृपया अपना ATM कार्ड डालें"
        )
    )
    print("======================================")

    card_number = input(
        t(
            "Enter Card Number: ",
            "कार्ड नंबर डालें: "
        )
    )

    con = connect_db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE card_number=%s",
        (card_number,)
    )

    user = cur.fetchone()

    cur.close()
    con.close()

    if user is None:

        print(t(
            "\nCard not found.",
            "\nकार्ड नहीं मिला।"
        ))

        pause()

        return None

    if user["status"] != "ACTIVE":

        print(t(
            "\nCARD IS BLOCKED.",
            "\nकार्ड ब्लॉक है।"
        ))

        pause()

        return None

    print(t(
        "\nCard detected.",
        "\nकार्ड पहचान लिया गया।"
    ))

    time.sleep(1)

    return user


# =====================================================
# PIN SET / GENERATE
# =====================================================

def set_pin(user):

    clear_screen()

    print("======================================")
    print(
        t(
            "PIN SETUP",
            "PIN सेट करें"
        )
    )
    print("======================================")

    print(
        t(
            "Create your 4-digit ATM PIN.",
            "अपना 4 अंकों का ATM PIN बनाएं।"
        )
    )

    while True:

        pin = input(
            t(
                "Enter new PIN: ",
                "नया PIN डालें: "
            )
        )

        if not pin.isdigit() or len(pin) != 4:

            print(t(
                "PIN must contain exactly 4 digits.",
                "PIN में ठीक 4 अंक होने चाहिए।"
            ))

            continue

        confirm_pin = input(
            t(
                "Confirm new PIN: ",
                "नया PIN दोबारा डालें: "
            )
        )

        if pin != confirm_pin:

            print(t(
                "PIN does not match.",
                "PIN match नहीं कर रहा।"
            ))

            continue

        break

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE users
        SET password=%s,
            pin_set=1,
            failed_attempts=0,
            status='ACTIVE'
        WHERE id=%s
        """,
        (pin, user["id"])
    )

    con.commit()

    cur.close()
    con.close()

    print(t(
        "\nPIN SET SUCCESSFULLY.",
        "\nPIN सफलतापूर्वक सेट हो गया।"
    ))

    pause()

    return True


# =====================================================
# PIN LOGIN
# =====================================================

def pin_login(user):

    # PIN not set
    if not user["pin_set"]:

        clear_screen()

        print(t(
            "Your PIN is not set.",
            "आपका PIN अभी सेट नहीं है।"
        ))

        choice = input(
            t(
                "Do you want to set PIN? (Y/N): ",
                "क्या आप PIN सेट करना चाहते हैं? (Y/N): "
            )
        )

        if choice.lower() == "y":

            return set_pin(user)

        return False

    # PIN already exists
    for attempt in range(3):

        clear_screen()

        print("======================================")
        print(
            t(
                "SECURITY VERIFICATION",
                "सुरक्षा जांच"
            )
        )
        print("======================================")

        pin = input(
            t(
                "Enter your 4-digit PIN: ",
                "अपना 4 अंकों का PIN डालें: "
            )
        )

        con = connect_db()
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT * FROM users WHERE id=%s",
            (user["id"],)
        )

        current_user = cur.fetchone()

        if pin == str(current_user["password"]):

            cur.execute(
                """
                UPDATE users
                SET failed_attempts=0
                WHERE id=%s
                """,
                (user["id"],)
            )

            con.commit()

            cur.close()
            con.close()

            print(t(
                "\nPIN VERIFIED.",
                "\nPIN सही है।"
            ))

            time.sleep(1)

            return True

        # Wrong PIN
        failed_attempts = (
            current_user["failed_attempts"] + 1
        )

        if failed_attempts >= 3:

            cur.execute(
                """
                UPDATE users
                SET failed_attempts=%s,
                    status='BLOCKED'
                WHERE id=%s
                """,
                (
                    failed_attempts,
                    user["id"]
                )
            )

            con.commit()

            cur.close()
            con.close()

            print(t(
                "\n3 wrong attempts.",
                "\n3 बार गलत PIN।"
            ))

            print(t(
                "Your card has been blocked.",
                "आपका कार्ड ब्लॉक कर दिया गया है।"
            ))

            pause()

            return False

        cur.execute(
            """
            UPDATE users
            SET failed_attempts=%s
            WHERE id=%s
            """,
            (
                failed_attempts,
                user["id"]
            )
        )

        con.commit()

        cur.close()
        con.close()

        print(t(
            f"\nWrong PIN. Attempts remaining: "
            f"{3 - failed_attempts}",
            f"\nगलत PIN। बाकी प्रयास: "
            f"{3 - failed_attempts}"
        ))

        pause()

    return False


# =====================================================
# RECORD TRANSACTION
# =====================================================

def record_transaction(
        account_number,
        transaction_type,
        amount,
        balance_after,
        receiver_account=None,
        status="SUCCESS"
):

    con = connect_db()
    cur = con.cursor()

    query = """
        INSERT INTO transactions
        (
            account_number,
            transaction_type,
            amount,
            balance_after,
            receiver_account,
            status
        )
        VALUES (%s,%s,%s,%s,%s,%s)
    """

    cur.execute(
        query,
        (
            account_number,
            transaction_type,
            amount,
            balance_after,
            receiver_account,
            status
        )
    )

    con.commit()

    cur.close()
    con.close()


# =====================================================
# GET BALANCE
# =====================================================

def get_balance(account_number):

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE id=%s",
        (account_number,)
    )

    result = cur.fetchone()

    cur.close()
    con.close()

    return float(result[0])


# =====================================================
# BALANCE INQUIRY
# =====================================================

def balance_inquiry(user):

    clear_screen()

    balance = get_balance(user["id"])

    print("======================================")
    print(
        t(
            "BALANCE INQUIRY",
            "बैलेंस की जानकारी"
        )
    )
    print("======================================")

    print(
        t(
            f"Available Balance : ₹{balance:.2f}",
            f"उपलब्ध बैलेंस : ₹{balance:.2f}"
        )
    )

    pause()


# =====================================================
# CASH WITHDRAWAL
# =====================================================

def cash_withdrawal(user):

    clear_screen()

    print("======================================")
    print(
        t(
            "CASH WITHDRAWAL",
            "कैश निकालें"
        )
    )
    print("======================================")

    print("1. ₹500")
    print("2. ₹1000")
    print("3. ₹2000")
    print("4. ₹5000")
    print("5. Other Amount")

    choice = input(
        t(
            "\nSelect amount: ",
            "\nराशि चुनें: "
        )
    )

    amount_list = {
        "1": 500,
        "2": 1000,
        "3": 2000,
        "4": 5000
    }

    if choice in amount_list:

        amount = amount_list[choice]

    elif choice == "5":

        try:

            amount = float(
                input(
                    t(
                        "Enter amount: ₹",
                        "राशि डालें: ₹"
                    )
                )
            )

        except ValueError:

            print(t(
                "Invalid amount.",
                "गलत राशि।"
            ))

            pause()
            return

    else:

        print(t(
            "Invalid option.",
            "गलत ऑप्शन।"
        ))

        pause()
        return

    if amount <= 0:

        print(t(
            "Invalid amount.",
            "गलत राशि।"
        ))

        pause()
        return

    # ATM notes simulation
    if amount % 100 != 0:

        print(t(
            "Amount must be multiple of ₹100.",
            "राशि ₹100 के गुणज में होनी चाहिए।"
        ))

        pause()
        return

    balance = get_balance(user["id"])

    if amount > balance:

        print(t(
            "Insufficient balance.",
            "पर्याप्त बैलेंस नहीं है।"
        ))

        pause()
        return

    new_balance = balance - amount

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE users
        SET balance=%s
        WHERE id=%s
        """,
        (
            new_balance,
            user["id"]
        )
    )

    con.commit()

    cur.close()
    con.close()

    record_transaction(
        user["id"],
        "WITHDRAW",
        amount,
        new_balance
    )

    print("\n" + t(
        "Processing...",
        "प्रोसेसिंग..."
    ))

    time.sleep(2)

    print("\n======================================")

    print(
        t(
            f"Please collect your cash: ₹{amount:.2f}",
            f"कृपया अपना कैश लें: ₹{amount:.2f}"
        )
    )

    print(
        t(
            f"Remaining Balance: ₹{new_balance:.2f}",
            f"बाकी बैलेंस: ₹{new_balance:.2f}"
        )
    )

    print("======================================")

    receipt(user, "CASH WITHDRAWAL", amount, new_balance)

    pause()


# =====================================================
# CASH DEPOSIT
# =====================================================

def cash_deposit(user):

    clear_screen()

    print("======================================")
    print(
        t(
            "CASH DEPOSIT",
            "कैश जमा करें"
        )
    )
    print("======================================")

    try:

        amount = float(
            input(
                t(
                    "Enter deposit amount: ₹",
                    "जमा राशि डालें: ₹"
                )
            )
        )

    except ValueError:

        print(t(
            "Invalid amount.",
            "गलत राशि।"
        ))

        pause()
        return

    if amount <= 0:

        print(t(
            "Invalid amount.",
            "गलत राशि।"
        ))

        pause()
        return

    balance = get_balance(user["id"])

    new_balance = balance + amount

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        """
        UPDATE users
        SET balance=%s
        WHERE id=%s
        """,
        (
            new_balance,
            user["id"]
        )
    )

    con.commit()

    cur.close()
    con.close()

    record_transaction(
        user["id"],
        "CASH DEPOSIT",
        amount,
        new_balance
    )

    print(t(
        "\nCash deposited successfully.",
        "\nकैश सफलतापूर्वक जमा हो गया।"
    ))

    print(
        t(
            f"New Balance: ₹{new_balance:.2f}",
            f"नया बैलेंस: ₹{new_balance:.2f}"
        )
    )

    receipt(
        user,
        "CASH DEPOSIT",
        amount,
        new_balance
    )

    pause()


# =====================================================
# FUND TRANSFER
# =====================================================

def fund_transfer(user):

    clear_screen()

    print("======================================")
    print(
        t(
            "FUND TRANSFER",
            "पैसे ट्रांसफर करें"
        )
    )
    print("======================================")

    try:

        receiver_account = int(
            input(
                t(
                    "Enter receiver account number: ",
                    "प्राप्तकर्ता का अकाउंट नंबर डालें: "
                )
            )
        )

    except ValueError:

        print(t(
            "Invalid account number.",
            "गलत अकाउंट नंबर।"
        ))

        pause()
        return

    if receiver_account == user["id"]:

        print(t(
            "You cannot transfer to your own account.",
            "आप अपने ही अकाउंट में पैसे ट्रांसफर नहीं कर सकते।"
        ))

        pause()
        return

    con = connect_db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id=%s
        AND status='ACTIVE'
        """,
        (receiver_account,)
    )

    receiver = cur.fetchone()

    if receiver is None:

        cur.close()
        con.close()

        print(t(
            "Receiver account not found.",
            "प्राप्तकर्ता का अकाउंट नहीं मिला।"
        ))

        pause()
        return

    try:

        amount = float(
            input(
                t(
                    "Enter transfer amount: ₹",
                    "ट्रांसफर राशि डालें: ₹"
                )
            )
        )

    except ValueError:

        cur.close()
        con.close()

        print(t(
            "Invalid amount.",
            "गलत राशि।"
        ))

        pause()
        return

    if amount <= 0:

        cur.close()
        con.close()

        print(t(
            "Invalid amount.",
            "गलत राशि।"
        ))

        pause()
        return

    sender_balance = float(
        get_balance(user["id"])
    )

    if amount > sender_balance:

        cur.close()
        con.close()

        print(t(
            "Insufficient balance.",
            "पर्याप्त बैलेंस नहीं है।"
        ))

        pause()
        return

    new_sender_balance = (
        sender_balance - amount
    )

    new_receiver_balance = (
        float(receiver["balance"]) + amount
    )

    # Sender
    cur.execute(
        """
        UPDATE users
        SET balance=%s
        WHERE id=%s
        """,
        (
            new_sender_balance,
            user["id"]
        )
    )

    # Receiver
    cur.execute(
        """
        UPDATE users
        SET balance=%s
        WHERE id=%s
        """,
        (
            new_receiver_balance,
            receiver_account
        )
    )

    con.commit()

    cur.close()
    con.close()

    # Sender transaction
    record_transaction(
        user["id"],
        "TRANSFER",
        amount,
        new_sender_balance,
        receiver_account
    )

    # Receiver transaction
    record_transaction(
        receiver_account,
        "TRANSFER RECEIVED",
        amount,
        new_receiver_balance,
        user["id"]
    )

    print(t(
        "\nTransfer successful.",
        "\nट्रांसफर सफल हुआ।"
    ))

    print(
        t(
            f"Transferred: ₹{amount:.2f}",
            f"ट्रांसफर राशि: ₹{amount:.2f}"
        )
    )

    print(
        t(
            f"Remaining Balance: ₹{new_sender_balance:.2f}",
            f"बाकी बैलेंस: ₹{new_sender_balance:.2f}"
        )
    )

    pause()


# =====================================================
# MINI STATEMENT
# =====================================================

def mini_statement(user):

    clear_screen()

    print("======================================")
    print(
        t(
            "MINI STATEMENT",
            "मिनी स्टेटमेंट"
        )
    )
    print("======================================")

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT
            transaction_type,
            amount,
            balance_after,
            transaction_date,
            status
        FROM transactions
        WHERE account_number=%s
        ORDER BY transaction_date DESC
        LIMIT 10
        """,
        (user["id"],)
    )

    rows = cur.fetchall()

    cur.close()
    con.close()

    if not rows:

        print(t(
            "No transactions found.",
            "कोई transaction नहीं मिला।"
        ))

        pause()
        return

    print(
        "\n{:<20} {:<12} {:<15}".format(
            "Transaction",
            "Amount",
            "Balance"
        )
    )

    print("-" * 50)

    for row in rows:

        transaction_type = row[0]
        amount = float(row[1])
        balance = float(row[2])

        print(
            "{:<20} ₹{:<11.2f} ₹{:<14.2f}".format(
                transaction_type,
                amount,
                balance
            )
        )

    pause()


# =====================================================
# CHANGE PIN
# =====================================================

def change_pin(user):

    clear_screen()

    print("======================================")
    print(
        t(
            "CHANGE PIN",
            "PIN बदलें"
        )
    )
    print("======================================")

    old_pin = input(
        t(
            "Enter old PIN: ",
            "पुराना PIN डालें: "
        )
    )

    con = connect_db()
    cur = con.cursor()

    cur.execute(
        "SELECT password FROM users WHERE id=%s",
        (user["id"],)
    )

    result = cur.fetchone()

    if old_pin != str(result[0]):

        cur.close()
        con.close()

        print(t(
            "Incorrect old PIN.",
            "पुराना PIN गलत है।"
        ))

        pause()
        return

    while True:

        new_pin = input(
            t(
                "Enter new 4-digit PIN: ",
                "नया 4 अंकों का PIN डालें: "
            )
        )

        if not new_pin.isdigit() or len(new_pin) != 4:

            print(t(
                "PIN must contain 4 digits.",
                "PIN में 4 अंक होने चाहिए।"
            ))

            continue

        confirm_pin = input(
            t(
                "Confirm new PIN: ",
                "नया PIN दोबारा डालें: "
            )
        )

        if new_pin != confirm_pin:

            print(t(
                "PIN does not match.",
                "PIN match नहीं कर रहा।"
            ))

            continue

        break

    cur.execute(
        """
        UPDATE users
        SET password=%s
        WHERE id=%s
        """,
        (
            new_pin,
            user["id"]
        )
    )

    con.commit()

    cur.close()
    con.close()

    print(t(
        "\nPIN changed successfully.",
        "\nPIN सफलतापूर्वक बदल गया।"
    ))

    pause()


# =====================================================
# RECEIPT
# =====================================================

def receipt(
        user,
        transaction_type,
        amount,
        balance
):

    print("\n--------------------------------------")

    choice = input(
        t(
            "Do you want a receipt? (Y/N): ",
            "क्या आपको रसीद चाहिए? (Y/N): "
        )
    )

    if choice.lower() != "y":
        return

    print("\n======================================")
    print("              ATM RECEIPT")
    print("======================================")

    print(
        "Account Number:",
        user["id"]
    )

    print(
        "Customer Name:",
        user["name"]
    )

    print(
        "Transaction:",
        transaction_type
    )

    print(
        f"Amount: ₹{amount:.2f}"
    )

    print(
        f"Balance: ₹{balance:.2f}"
    )

    print(
        "Date:",
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )
    )

    print("======================================")


# =====================================================
# ATM MAIN MENU
# =====================================================

def atm_menu(user):

    while True:

        clear_screen()

        print("======================================")
        print(
            t(
                "             ATM MENU",
                "             ATM मेनू"
            )
        )
        print("======================================")

        print(
            t(
                f"Welcome {user['name']}",
                f"स्वागत है {user['name']}"
            )
        )

        print("\n1.",
              t(
                  "Cash Withdrawal",
                  "कैश निकालें"
              ))

        print("2.",
              t(
                  "Balance Inquiry",
                  "बैलेंस देखें"
              ))

        print("3.",
              t(
                  "Cash Deposit",
                  "कैश जमा करें"
              ))

        print("4.",
              t(
                  "Fund Transfer",
                  "पैसे ट्रांसफर करें"
              ))

        print("5.",
              t(
                  "Mini Statement",
                  "मिनी स्टेटमेंट"
              ))

        print("6.",
              t(
                  "Change PIN",
                  "PIN बदलें"
              ))

        print("7.",
              t(
                  "Exit",
                  "बाहर निकलें"
              ))

        choice = input(
            t(
                "\nSelect transaction: ",
                "\nTransaction चुनें: "
            )
        )

        if choice == "1":

            cash_withdrawal(user)

        elif choice == "2":

            balance_inquiry(user)

        elif choice == "3":

            cash_deposit(user)

        elif choice == "4":

            fund_transfer(user)

        elif choice == "5":

            mini_statement(user)

        elif choice == "6":

            change_pin(user)

        elif choice == "7":

            print("\n======================================")

            print(
                t(
                    "Please take your card.",
                    "कृपया अपना कार्ड निकाल लें।"
                )
            )

            time.sleep(1)

            print(
                t(
                    "Thank you for using our ATM.",
                    "हमारे ATM का उपयोग करने के लिए धन्यवाद।"
                )
            )

            print("======================================")

            time.sleep(2)

            return

        else:

            print(t(
                "Invalid option.",
                "गलत ऑप्शन।"
            ))

            pause()


# =====================================================
# MAIN PROGRAM
# =====================================================

def main():

    while True:

        select_language()

        clear_screen()

        print("======================================")
        print("                 ATM")
        print("======================================")

        print(
            "\n1.",
            t(
                "Insert Card",
                "कार्ड डालें"
            )
        )

        print(
            "2.",
            t(
                "Create New Account",
                "नया अकाउंट बनाएं"
            )
        )

        print(
            "3.",
            t(
                "Exit",
                "बाहर निकलें"
            )
        )

        choice = input(
            t(
                "\nSelect option: ",
                "\nऑप्शन चुनें: "
            )
        )

        # INSERT CARD
        if choice == "1":

            user = insert_card()

            if user is not None:

                if pin_login(user):

                    atm_menu(user)

        # NEW ACCOUNT
        elif choice == "2":

            create_account()

        # EXIT
        elif choice == "3":

            print(t(
                "\nThank you. Goodbye!",
                "\nधन्यवाद। फिर मिलेंगे!"
            ))

            break

        else:

            print(t(
                "\nInvalid option.",
                "\nगलत ऑप्शन।"
            ))

            pause()


# =====================================================
# PROGRAM START
# =====================================================

if __name__ == "__main__":
    main()