# utils.py

import getpass
import sqlite3
import csv
import matplotlib.pyplot as plt
import pandas as pd
import re


RED='\033[91m '
GREEN='\033[92m'
END ='\033[0m'
PURPLE = '\033[95m'
BLUE = '\033[94m'

         
 
# 创建数据库连接
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()

# Create user table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
''')

# Create data table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        type TEXT,
        source TEXT,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# register
def register():
    try:
        username = input("Enter username: ")
        password = getpass.getpass("Enter password (Due to your privacy, your password will not be shown): ")

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            # clear_screen()
            print(RED+"Username already exists. "+END+"Please choose a different username.")
            return

        # Insert user information into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        # clear_screen()
        print(GREEN+ "Registration successful!"+ END+ "\U0001F60E")
    except Exception as e:
        print("Error during registration:", str(e))

# login
def login():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password (Due to your privacy, your password will not be shown): ")

    # Verify username and password
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user_id = cursor.fetchone()
    if user_id:
        # clear_screen()
        print(GREEN+"Login successful" + END+ " \U0001F60E")
        return user_id[0]  # Return the user_id
    
    else:
        # clear_screen()
        print(RED+"Invalid username or password." + END+ " \U0001F635")
        return None

# income & expense record
def record_transaction(user_id):
    amount = float(input("Enter amount ("+RED+"please input number "+END+"):"))
    category = input("Enter category: ")
    transaction_type = input("Enter type (income/expense): ")
    date = input("Enter date (YYYY-MM-DD): ")

    # 将交易信息插入数据库
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, category, type, date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, category, transaction_type, date))
    conn.commit()
    print(GREEN+'Transaction recorded successfully'+ END)
# CSV record
def import_transactions(user_id):
    file_path = input("Enter file path: ")

    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            transactions = []
            
            # Print column names for debugging
            print("CSV Columns:", reader.fieldnames)

            for row in reader:
                amount = float(row['Amount'])  # Verify the field name is correct
                category = row['Category']
                type = row['Type']
                source = row['Source']
                date = row['Date']
                transactions.append((user_id, amount, category, type, source, date))

                # Print transactions for debugging
                print("Transactions to be inserted:", transactions)

                # This is to insert transactions into the database
            cursor.executemany("""
                INSERT INTO transactions (user_id, amount, category, type, source, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, transactions)
            conn.commit()

            print(GREEN+"Transactions imported successfully"+END)
    except FileNotFoundError:
        print(RED+"File not found."+END)
    except csv.Error as e:
        print(RED+f"Error reading CSV file: {e}"+END)
    except Exception as e:
        print(RED+"Error during transaction import:", str(e)+END)
        
# reyurn database into a list of list
def get_transcations(user_id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # Execute query
    cursor.execute("""
        SELECT date, type, amount, category, source FROM transactions
        WHERE user_id = ?
    """, (user_id,))

    # Get query results
    transactions = cursor.fetchall()

    whole_list=[]
    for transaction in transactions:
        a=list(transaction)
        a[1],a[3]=a[3],a[1]
        del a[4]
        whole_list.append(a)   
    return whole_list

# Summarize
def summarize_transactions(user_id):
    cursor.execute("""
    SELECT SUBSTR(date, 1, 7) AS month,
        SUM(CASE WHEN type='Income' THEN CAST(amount AS REAL) ELSE 0.0 END) AS total_income,
        SUM(CASE WHEN type='Expense' THEN CAST(amount AS REAL) ELSE 0.0 END) AS total_expense
    FROM transactions
    WHERE user_id=?
    GROUP BY month
    """, (user_id,))

    print("Monthly Summary:")
    print("--------------")
    print("{:<10} {:<15} {:<15}".format("Month", "Total Income", "Total Expense"))
    print("-" * 40)
    for row in cursor.fetchall():
        month = row[0]
        total_income = row[1]
        total_expense =row[2]
        print("{:<10} {:<15} {:<15}".format(month, total_income, total_expense))

    # Fetching category-wise expense totals
    cursor.execute("""
        SELECT category, SUM(amount) AS total_expense
        FROM transactions
        WHERE user_id=? AND type='Expense'
        GROUP BY category
    """, (user_id,))

    print("\nExpense Summary by Category:")
    print("-----------------------------")
    print("{:<20} {:<15}".format("Category", "Total Expense"))
    print("-" * 40)
    for row in cursor.fetchall():
        category = row[0]
        total_expense = row[1]
        print("{:<20} {:<15}".format(category, total_expense))

def data_analysis(user_id):
    # try:
    # Summarizing transactions
    cursor.execute("""
        SELECT SUBSTR(date, 1, 7) AS month,
            SUM(CASE WHEN type='Income' THEN CAST(amount AS REAL) ELSE 0.0 END) AS total_income,
            SUM(CASE WHEN type='Expense' THEN CAST(amount AS REAL) ELSE 0.0 END) AS total_expense
        FROM transactions
        WHERE user_id=?
        GROUP BY month
    """, (user_id,))

    print("Monthly Summary:")
    print("--------------")
    print("{:<10} {:<15} {:<15}".format("Month", "Total Income", "Total Expense"))
    print("-" * 40)
    for row in cursor.fetchall():
        month = row[0]
        total_income = row[1]
        total_expense =row[2]
        print("{:<10} {:<15} {:<15}".format(month, total_income, total_expense))

    # Fetching category-wise expense totals
    cursor.execute("""
        SELECT category, SUM(amount) AS total_expense
        FROM transactions
        WHERE user_id=? AND type='Expense'
        GROUP BY category
    """, (user_id,))

    print("\nExpense Summary by Category:")
    print("-----------------------------")
    print("{:<20} {:<15}".format("Category", "Total Expense"))
    print("-" * 40)
    for row in cursor.fetchall():
        category = row[0]
        total_expense = row[1]
        print("{:<20} {:<15}".format(category, total_expense))

    # Fetching category-wise expense totals for visualization
    cursor.execute("""
        SELECT category, SUM(amount) AS expense
        FROM transactions
        WHERE user_id=? AND type='Expense'
        GROUP BY category
    """, (user_id,))

    categories = []
    expenses = []

    for row in cursor.fetchall():
        categories.append(row[0])
        expenses.append(row[1])
    expensess = sum(expenses)
    # Creating a pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(expenses, labels=categories, autopct='%1.1f%%')
    plt.title("Spending Patterns by Category")
    plt.text(-1.5, 1, f"Total Incomes: ${total_income}", fontsize=12, color='green')
    plt.text(1, 1, f"Total Expenses: ${expensess}", fontsize=12, color='red')
    plt.show()

    # Creating a bar graph
    plt.figure(figsize=(10, 5))
    plt.bar(categories, expenses)
    plt.xlabel("Category")
    plt.ylabel("Total Expense")
    plt.title("Spending Patterns by Category")
    plt.xticks(rotation='horizontal')
    plt.text(-0.5, 220, f"Total Incomes: ${total_income}", fontsize=12, color='green')
    plt.text(2, 220, f"Total Expenses: ${expensess}", fontsize=12, color='red')
    plt.show()
    return

# Visulizer
def Visualiser(expenses_list):
    Month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def onemonth_merge(expenses_list, month, user_year_choice):
        month = month.zfill(2)
        monthly_list = [entry[3:] for entry in [re.split(r'[-/]', entry[0]) + entry[1:] for entry in expenses_list if re.split(r'[-/]', entry[0])[1] == month and re.split(r'[-/]', entry[0])[0] == user_year_choice]]
        for i in range(len(monthly_list)):
            for j in range(i + 1, len(monthly_list)):
                if monthly_list[i][0] == monthly_list[j][0] and monthly_list[i][2] == monthly_list[j][2]:
                    monthly_list[i][1] += monthly_list[j][1]
                    monthly_list[j][1] = 0
        monthly_list = [entry for entry in monthly_list if entry[1] != 0]

        dic = {'transactions': [], 'Income': [], 'Expense': []}
        for entry in monthly_list:
            dic['transactions'].append(entry[0])
            dic['Income'].append(entry[1] if entry[2] == 'Income' else 0)
            dic['Expense'].append(entry[1] if entry[2] == 'Expense' else 0)
        return dic
    def draw_onemonth(dic, month):
        if not dic['transactions']:
            
            plt.title(RED+f"No data available for {Month[int(month) - 1]}"+END)
            plt.show()
            return
        
        numeric_data_available = any(isinstance(value, (int, float)) for value in dic['Income'] + dic['Expense'])
        if not numeric_data_available:
            print(RED+f"No numeric data available for {Month[int(month) - 1]}"+END)
            return

        plot = pd.DataFrame(dic)
        ax = plot.plot(x='transactions', y=["Income", "Expense"], kind="bar")
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
        plt.title(f'{Month[int(month) - 1]}.{user_year_choice} Financial Report (Close the chart to see the report)')
        plt.show()

    def annual_merge(expenses_list, year):
        annual_list = [entry for entry in [entry for entry in expenses_list if re.split(r'[-/]', entry[0])[0] == year]]
        dic = {'month': [], 'Income': [], 'Expense': []}
        monthly_totals = {}

        for entry in annual_list:
            month = int(re.split(r'[-/]', entry[0])[1])
            
            if month not in monthly_totals:
                monthly_totals[month] = {'Income': 0, 'Expense': 0}
            
            monthly_totals[month]['Income'] += entry[2] if entry[3] == 'Income' else 0
            monthly_totals[month]['Expense'] += entry[2] if entry[3] == 'Expense' else 0

        for month, totals in monthly_totals.items():
            dic['month'].append(month)
            dic['Income'].append(totals['Income'])
            dic['Expense'].append(totals['Expense'])

        return dic
    def draw_annual(dic, year, expenses_list):
        if not dic['month']:
            print(RED+f"No data available for the year {year}"+END)
            return

        numeric_data_available = any(isinstance(value, (int, float)) for value in dic['Income'] + dic['Expense'])
        if not numeric_data_available:
            print(RED+f"No numeric data available for the year {year}"+END)
            return
        
        df = pd.DataFrame({
            'Month': list(range(1, 13)),
            'Income': [0] * 12,
            'Expense': [0] * 12
        })

        for i, month in enumerate(dic['month']):
            df.at[month - 1, 'Income'] = dic['Income'][i]
            df.at[month - 1, 'Expense'] = dic['Expense'][i]
        plt.figure(figsize=(10, 6))
        plt.plot(df['Month'], df['Income'], marker='o', label='Income', linestyle='-', color='green')
        plt.plot(df['Month'], df['Expense'], marker='o', label='Expense', linestyle='-.', color='red')

        for i, txt in enumerate(df['Income']):
            plt.annotate(txt, (df['Month'][i], df['Income'][i]), textcoords="offset points", xytext=(0, 5), ha='center')

        for i, txt in enumerate(df['Expense']):
            plt.annotate(txt, (df['Month'][i], df['Expense'][i]), textcoords="offset points", xytext=(0, -15), ha='center', color='red')

        plt.title(f'Annual Financial Report for {year}')
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.legend()
        plt.show()

    def plot_expenses(expenses_list):
        from collections import defaultdict
        from datetime import datetime
        import matplotlib.pyplot as plt

        # Create a dictionary to store data for each year
        year_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'categories': defaultdict(float)})

        # Parse the data and update the dictionary
        for entry in expenses_list:
            date_str, category, amount, type = entry
            date = datetime.strptime(date_str, '%Y/%m/%d') if '/' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
            year = str(date.year)
            year_data[year]['categories'][category] += amount

            if type == 'Income':
                year_data[year]['income'] += amount
            elif type == 'Expense':
                year_data[year]['expense'] += amount

        # Combine all years into one figure
        fig, axes = plt.subplots(nrows=len(year_data), ncols=1, figsize=(10, 8 * len(year_data)))

        # Ensure axes is always a list
        if len(year_data) == 1:
            axes = [axes]

        for i, (year, values) in enumerate(year_data.items()):
            categories = list(values['categories'].keys())
            amounts = list(values['categories'].values())
            total_income = values['income']
            total_expense = values['expense']

            # Plot pie chart for income and expenses combined
            ax = axes[i]
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.set_title(f'Year {year} - Total Income: {total_income}, Total Expense: {total_expense}')

        plt.tight_layout()
        plt.show()


    # Main
    user_choice = input("1️⃣  - CERTAIN MONTH incomes vs. expenses ("+GREEN+"Bar Chart"+END+")\n2️⃣  - MONTHLY incomes vs. expenses ("+BLUE+"Line Chart"+END+")\n3️⃣  - ANNUAL incomes vs. expenses ("+PURPLE+"Pie Chart"+END+")\nChoose one type:")
    if user_choice == '1':
        user_year_choice = input("Enter the year you want to see ("+GREEN+"e.g., 2023"+END+"): ")
        
        while True:
            print("1 - Jan; 2 - Feb; 3 - Mar; 4 - Apr; 5 - May; 6 - Jun; 7 - July; 8 - August; 9 - Sept; 10 - Oct; 11 - Nov; 12- Dec")
            user_month_choice = input("Choose a certain month you want to see (13 - "+GREEN+"Rechoose the year"+END+"; 14 - "+RED+"Exit"+END+"):")
            print(f"User month choice: {user_month_choice}")
            
            if user_month_choice == '13':
                user_year_choice = input("Enter the year you want to see ("+GREEN+"e.g., 2023"+END+"): ")
                print("1 - Jan; 2 - Feb; 3 - Mar; 4 - Apr; 5 - May; 6 - Jun; 7 - July; 8 - August; 9 - Sept; 10 - Oct; 11 - Nov; 12- Dec")
                user_month_choice = input("Choose the month you want to see (13 - "+GREEN+"Rechoose the year"+END+"; 14 - "+RED+"Exit"+END+"):")
                
            if user_month_choice == '14':
               break
            a = onemonth_merge(expenses_list, user_month_choice, user_year_choice)
            draw_onemonth(a, user_month_choice)

    elif user_choice == '2':
        user_year_choice = input("Enter the year you want to see what you spend and income MONTHLY("+GREEN+"e.g., 2023"+END+"):")
        a = annual_merge(expenses_list, user_year_choice)
        draw_annual(a, user_year_choice, expenses_list)
    
    elif user_choice == '3':
        plot_expenses(expenses_list)
    
def optimizeandgoals(user_id):
    # Fetching category-wise expense averages for cost optimization
    cursor.execute("""
        SELECT category, AVG(amount) AS avg_expense
        FROM transactions
        WHERE user_id=? AND type='Expense'
        GROUP BY category
    """, (user_id,))

    categories = []
    avg_expenses = []

    #create avg expense for each category
    print("\nAverage Expense by Category:")
    print("-----------------------------")
    print("{:<20} {:<15}".format("Category", "avg_expense"))
    print("-" * 40)
    for row in cursor.fetchall():
        category = row[0]
        avg_expense = row[1]
        categories.append(category)
        avg_expenses.append(avg_expense)
        print("{:<20} {:<15}".format(category, avg_expense))

    # Calculating the total average expense
    total_avg_expense = round(sum(avg_expenses) / len(avg_expenses),2)
    print("\nTotal Average Expense:", total_avg_expense)
    print("-----------------------------")
    print("-----------------------------\n")



    # Finding categories where expenses are above the average
    above_average_categories = []
    for i in range(len(categories)):
        if avg_expenses[i] > total_avg_expense:
            above_average_categories.append(categories[i])

    print("Categories with Above Average Expenses:")
    print("--------------------------------------")
    for category in above_average_categories:
        print(category)

    # Fetching total income and expenses
    cursor.execute("""
        SELECT SUM(CASE WHEN type='Income' THEN CAST(amount AS REAL) ELSE 0.0 END) AS total_income,
            SUM(CASE WHEN type='Expense' THEN CAST(amount AS REAL) ELSE 0.0 END) AS total_expense
        FROM transactions
        WHERE user_id=?
    """, (user_id,))


    row = cursor.fetchone()
    total_income = row[0]
    total_expense = row[1]

    # Tell them the total income and expenses
    print("Total Income: $", total_income)
    print("Total Expense: $", total_expense)

    #Then ask to set financial goals
    goal = float(input("\nEnter your financial goal: "))

    # Calculate the progress towards the goal
    progress = (total_income - total_expense) / goal * 100

    print("Financial Goal Progress:")
    print("------------------------")
    print("Goal: $", goal)
    print("Progress: ", round(progress, 2), "%") 

def optimize(expenses_list):
    def choose_category():
        unique_categories = set()
        for entry in expenses_list:
            if entry[3] == 'Expense':
                unique_categories.add(entry[1])
        unique_categories = list(unique_categories)  # Convert set to list for indexing
        for i, category in enumerate(unique_categories):
            print(f"{i + 1}. {category}")
        print("Please choose a category "+GREEN+"NUMBER"+END+" (the above categories are where you have expenses):")
        choice = int(input()) - 1  # Adjusting the choice to match the list index
        return choice, unique_categories  # Return both choice and unique_categories

    def calculate_average(category):
        expenses = [entry[2] for entry in expenses_list if entry[1] == category]
        if not expenses:
            return 0
        else:
            return sum(expenses) / len(expenses)

    def add_expense(category_index, unique_categories):
        category_name = unique_categories[category_index]  # Get the category name
        expense = float(input(f"Please enter the next time you probably in {category_name} consumption: "))
        for entry in expenses_list:
            if entry[1] == category_name:
                entry[2] = expense  # Update the expense for the correct category
                break


        
    def check_expense(category):
        average = calculate_average(expenses_list[category][1])
        print("Your average expense in this catagory is",average)
        latest_expense = expenses_list[category][2]
        if latest_expense > average:
            print("Your last expense is higher than the average. I suggest you reduce your expense a little.")
        else:
            print("Good job. Please keep it up.")
            
    def main():
        category_index, unique_categories = choose_category()
        add_expense(category_index, unique_categories)
        check_expense(category_index)

    main()

# Main FUnction
def main():
    user_id = None

    while user_id is None:

        choice = input("\U0001F978 "+"  Choose an option:  1️⃣  - Register, 2️⃣  - Login, 3️⃣  - Exit\n")

        if choice == '1':
            register()
        elif choice == '2':
            user_id = login()
        elif choice == '3':
            print(GREEN+"Goodbye!"+END)
            conn.close()
            return
        else:
            print(RED+"Invalid choice. Please try again."+END+" \U0001F635")

    while True:
        option = input("\U0001F978"+"""  Choose an option:
        1️⃣  - Record transactions
        2️⃣  - Import transactions
        3️⃣  - Summarize and Visualize transactions
        4️⃣  - Optimize Categories and Set Goals
        5️⃣  - Exit\n""")

        if option == '1':
            record_transaction(user_id)
            
        elif option == '2':
            import_transactions(user_id)
            
        elif option == '3':
            n=int(input("1️⃣  - "+PURPLE+"Summarize"+END+" on terminal\n2️⃣  - "+BLUE+"Visualize"+END+" on charts\n3️⃣  - "+PURPLE+"Summare"+END+" +"+BLUE+" Visualize "+END+"the whole records\nChoose One Type:"))
            if n==1:summarize_transactions(user_id) #Summarize
            if n==2: Visualiser(get_transcations(user_id)) #Charts
            if n==3: data_analysis(user_id) #Charts+Summarize
        elif option == '4':
            n=int(input("choose the Optimize type:\n1️⃣  - Set your future "+PURPLE+"INCOME"+END+" goal 2️⃣  - See if this time u will overspend/below the average "+BLUE+"EXPENSE"+END+"\nChoose One Type:"))
            if n==1:optimizeandgoals(user_id)
            if n==2:optimize(get_transcations(user_id))
            else: print(RED+"Wrong choices"+END)
            
        elif option == '5':
            # clear_screen()
            print(GREEN+"Goodbye!"+END)
            conn.close()
            return
        
        else:
            print(RED+"Invalid option."+END+" Please try again."+" \U0001F635")

if __name__ == '__main__':
    main()
    
