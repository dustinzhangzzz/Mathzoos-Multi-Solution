import re
import psycopg2
import unicodedata

class ArgumentsExtractor:
    # code with pattern matching using regular expression

    # 6/3/2024 - finished up until kp76 | can run test cases,update patterns and fix kp49,58,64,66,73
    # 6/5/2024 - finished patterns,ran test cases,fixed overlapping patterns & special cases | check 30,run all test cases,figure out 5,11,16
    # 6/5/2024 - fixed logic for all except 74,64-66

    # Skipped kp on StackEdit - 5,8,11,12,16,20,37,53,56,58(*),64(*),66(*)

    def extract_args_final(self, sql_string, knowledgepoint_id):
        if knowledgepoint_id == 68:
            sql_string = sql_string.split('\\n')[1]
            sql_string = sql_string.replace("Solve.\n", "").replace(" = [[ans]]", "")

            # Step 2: Remove the $ symbols around the numbers
            sql_string = re.sub(r'\$', '', sql_string)
            sql_string = sql_string.replace('−', '-')
            # Step 3: Replace mathematical symbols
            sql_string = sql_string.replace('×', '*').replace('÷', '/')
            sql_string = sql_string.replace(" ", "")
            #print(sql_string)
            return {"arg1":sql_string}
        if knowledgepoint_id == 46:
            match = re.search(r"\d+\.\d+", sql_string)
            if match:
                decimal = float(match.group(0))
                return {"arg1" : decimal}
            else:
                return {"arg1" : 0.0}
        if knowledgepoint_id == 57:
            def convert_mixed_number(mixed_number):
                """Convert a mixed number in the form 'a\\frac{b}{c}' to its components."""
                parts = re.match(r'(\d+)\\frac{(\d+)}{(\d+)}', mixed_number)
                if parts:
                    whole = int(parts.group(1))
                    numerator = int(parts.group(2))
                    denominator = int(parts.group(3))
                    return whole, numerator, denominator
                return None, None, None

            def convert_expression(input_string):
                # Normalize the input to handle any special encoding issues
                input_string = unicodedata.normalize('NFKD', input_string)

                # Remove 'Solve.##If your answer is an improper fraction, write it as a mixed number.\n'
                result = re.sub(r'Solve\.##If your answer is an improper fraction, write it as a mixed number\.\n', '',
                                input_string)
                # Remove dollar signs and spaces
                result = result.replace('$', '').replace(' ', '').replace('\n', '')

                # Determine if the operation is addition or subtraction
                is_subtraction = '−' in result

                # Remove the operation sign for extraction
                result = result.replace('−', '').replace('+', '')

                # Extract the mixed numbers
                mixed_numbers = re.findall(r'(\d+\\frac{\d+}{\d+})', result)

                if len(mixed_numbers) != 2:
                    raise ValueError("Unexpected input format. Expected two mixed numbers.")

                # Convert mixed numbers to their components
                whole1, num1, den1 = convert_mixed_number(mixed_numbers[0])
                whole2, num2, den2 = convert_mixed_number(mixed_numbers[1])

                if whole1 is None or whole2 is None:
                    raise ValueError("Error parsing mixed numbers.")

                # Handle the sign of the second mixed number based on the operation
                if is_subtraction:
                    whole2 = -whole2

                # Format the args dictionary
                args_dict = {
                    'arg1': whole1,
                    'arg2': num1,
                    'arg3': den1,
                    'arg4': whole2,
                    'arg5': num2,
                    'arg6': den2
                }

                # Convert dictionary to string


                return args_dict
            return convert_expression(sql_string)

        if knowledgepoint_id == 71 or knowledgepoint_id == 69:
            def convert_fraction(fraction):
                """Convert a fraction in the form '\\frac{a}{b}' to its components."""
                parts = re.match(r'\\frac{(\d+)}{(\d+)}', fraction)
                if parts:
                    numerator = int(parts.group(1))
                    denominator = int(parts.group(2))
                    return numerator, denominator
                else:
                    numerator = int(fraction)
                    denominator = 1
                    return numerator, denominator
                return None, None

            def convert_expression(input_string, knowledgepoint_id):
                # Normalize the input to handle any special encoding issues
                input_string = unicodedata.normalize('NFKD', input_string)

                # Remove 'Solve.##If your answer is an improper fraction, write it as a mixed number.\n'
                if knowledgepoint_id == 69:
                    result = re.sub(r'Solve\.##Reduce the answer to the lowest term\.\n', '',
                                    input_string)
                else:
                    result = re.sub(r'Solve\.##If your answer is an improper fraction, write it as a mixed number\.\n',
                                    '',
                                    input_string)
                # Remove dollar signs and spaces
                result = result.replace('$', '').replace(' ', '').replace('\n', '')

                # Extract fractions and operations
                fractions = re.findall(r'\\frac{\d+}{\d+}|\d+', result)
                if knowledgepoint_id == 69:
                    operations = re.findall(r'[\×\÷]', result)
                else:
                    operations = re.findall(r'[\+\−]', result)
                operations[0] = operations[0].replace("×",'x').replace('÷', '/')
                operations[1] = operations[1].replace("×", 'x').replace('÷', '/')
                if len(fractions) != 3 or len(operations) != 2:
                    raise ValueError(fractions, operations, "Unexpected input format. Expected three fractions and two operations.")

                # Convert fractions to their components
                num1, den1 = convert_fraction(fractions[0])
                num2, den2 = convert_fraction(fractions[1])
                num3, den3 = convert_fraction(fractions[2])

                if num1 is None or num2 is None or num3 is None:
                    raise ValueError("Error parsing fractions.")

                # Format the args dictionary
                args_dict = {
                    'arg1': num1,
                    'arg2': den1,
                    'arg3': num2,
                    'arg4': den2,
                    'arg5': num3,
                    'arg6': den3,
                    'arg7': operations[0],
                    'arg8': operations[1]
                }

                # Convert dictionary to string
                return args_dict

            return convert_expression(sql_string, knowledgepoint_id)
        args_dict = {"arg1": ""}
        prefix = """Fill in the missing numbers"""
        if sql_string.startswith(prefix):
            # Remove the starting substring
            text = sql_string[len(prefix) + 3:]
            result = re.sub(r'\[\[ans\]\]', '_', text)
            result = re.sub(r'\s*,\s*', ',', result)
            args_dict["arg1"] = result
            return args_dict

        if knowledgepoint_id == 72 or knowledgepoint_id == 73:
            def convert_fraction(fraction):
                """Convert a fraction in the form '\\frac{a}{b}' to its components."""
                parts = re.match(r'\\frac{(\d+)}{(\d+)}', fraction)
                if parts:
                    numerator = int(parts.group(1))
                    denominator = int(parts.group(2))
                    return numerator, denominator
                return None, None

            def convert_expression(*args):
                # Handle both one and two argument inputs
                if len(args) == 1:
                    input_string = args[0]
                    first_dollar_index = input_string.find('$')
                    if first_dollar_index != -1:
                        input_string = input_string[first_dollar_index:]
                elif len(args) == 2:
                    input_string = args[1]
                else:
                    raise ValueError("Invalid number of arguments. Provide either one or two arguments.")

                # Normalize the input to handle any special encoding issues
                input_string = unicodedata.normalize('NFKD', input_string)

                # Extract the fractions and operations
                fractions = re.findall(r'\\frac{\d+}{\d+}', input_string)
                operations = re.findall(r'[\+\−÷×]', input_string)

                # Convert fractions to their components
                num1, den1 = convert_fraction(fractions[0])
                num2, den2 = convert_fraction(fractions[1])
                num3, den3 = convert_fraction(fractions[2])

                # Check if the fourth fraction exists
                if len(fractions) == 4:
                    num4, den4 = convert_fraction(fractions[3])
                else:
                    num4, den4 = None, None

                if num1 is None or num2 is None or num3 is None:
                    raise ValueError("Error parsing fractions.")

                # Map operation symbols to desired output
                operation_map = {
                    '+': '+',
                    '−': '-',
                    '÷': '/',
                    '×': '*'
                }

                # Format the expression
                if num4 is not None and den4 is not None:
                    expression = f"([{num1}|{den1}]{operation_map[operations[0]]}[{num2}|{den2}]{operation_map[operations[1]]}[{num3}|{den3}]){operation_map[operations[2]]}[{num4}|{den4}]"
                else:
                    expression = f"([{num1}|{den1}]{operation_map[operations[0]]}[{num2}|{den2}]{operation_map[operations[1]]}[{num3}|{den3}])"

                return expression

            # Example input string
            args_dict["arg1"] = convert_expression(sql_string)
            return args_dict

        # difficult kp - 5,11,16 | Null or DNE on StackEdit/pgAdmin - 8,20
        pattern1 = r'\$(\d+)\$\s+(tens|ones|hundreds)'  # 1,2,18 - $d$ wwww
        pattern2 = r'\"([^\"]+)\"'  # for the other half of 19 - square brackets rep character class/^ negates
        pattern3 = r'\{*\$*(\d+\.\d+|\d+)\$*\}*'  # all other cases (test 30)

        matches1 = re.findall(pattern1, sql_string)
        matches2 = re.findall(pattern2, sql_string)
        matches3 = re.findall(pattern3, sql_string)




        if len(matches1) > 0:
            counter = 1
            for match in matches1:
                args_dict["arg" + str(counter)] = int(match[0])
                args_dict["arg" + str(counter + 1)] = match[1]
                counter += 2
            return args_dict

        elif len(matches2) > 0:  # one arg for 19
            args_dict["arg1"] = matches2[0]
            return args_dict

        elif len(matches3) > 0:
            phrases = ["Find the mean", "sorting in order", "appears the most"]  # 64,65,66 respectively
            for phrase in phrases:
                if phrase in sql_string:
                    args_dict["arg1"] = matches3
                    return args_dict
            if "Add.##If your answer is an improper fraction, change it to a mixed number." in sql_string or "Subtract the fractions.##If your answer is an improper fraction, change it to a mixed number." in sql_string:  # wording for 49,50
                args_dict["arg1"] = int(matches3[1])
                args_dict["arg2"] = int(matches3[0])
                args_dict["arg3"] = int(matches3[2])
            else:  # any other question
                for i in range(len(matches3)):
                    try:
                        args_dict["arg" + str(i + 1)] = int(matches3[i])
                    except ValueError:
                        args_dict["arg" + str(i + 1)] = float(matches3[i])


        return args_dict

    def extract_test_cases_from_database(connection_string, query):
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()  # connect to the PostgreSQL database

        cursor.execute(query)  # execute the SQL query to retrieve the strings

        rows = cursor.fetchall()  # fetch all rows of data

        connection.close()  # close the database connection

        test_cases = [row[0] for row in rows]  # extract the strings from the rows
        return test_cases

    def run_test_cases(self, test_cases):
        for test_case in test_cases:
            result = self.extract_args_final(test_case)
            print("Test Case: {}".format(test_case))
            print("Result: {}\n".format(result))

# if __name__ == "__main__": #need to instantiate before calling method since extract_args is an instance method (or make static)
#     connection_string = "dbname='MathZoosTest' user='postgres' host='34.125.112.255' port='5433' password='oB7CLEUve9w6xNwHNLAdqw'" #dbname is usually same as user
#     query = '''WITH min_questions AS (
#     SELECT
#         MIN(question_id) AS question_id,
#         knowledge_point_id
#     FROM
#         public."Question"
#     GROUP BY
#         knowledge_point_id
#     )
#     SELECT
#         q.question_text
#     FROM
#         min_questions mq
#     JOIN
#         public."Question" q
#     ON
#         mq.question_id = q.question_id
#     ORDER BY
#         q.knowledge_point_id ASC;''' #grabs a question from each knowledge point
#
#     ra=ReturnArg()
#     test_cases = ReturnArg.extract_test_cases_from_database(connection_string, query) #extract_test_case method is static, so no need instance
#
#     ra.run_test_cases(test_cases)

# Notes:
# some knowledgepoints on pgAdmin are null (no kp 20), 38/59/63 skipped on StackEdit but exist on pgAdmin
# code only works for half of 19, other half are in word form [would this be four args? "five hundred thirty seven"]) -> the whole quotation is one arg
# kp25 on pgAdmin diff from k25 on StackEdit (used one on pgAdmin) -> base on pgAdmin
# for kp49, 10/19 + 5/19 would be three or four args? -> same denominator so 3 args
# kp58 switches order - not sure how to write that specifically -> just retrieve the two values
# kp64,66 - one arg or three args? StackEdit says one arg -> only one arg, value = string of the three numbers separated by comma (same for 66)
# kp73 has a combination of improper and mixed numbers
# **Finish up until kp76 | Run test cases through code to check extracted arg
# kp 18 similar to 1 but have 2 or three arguments

# Notes on sql:
# had to download PostGreSQL and update path to PostGreSQL bin directory to run psql from any command prompt
# run return_arg.py from command prompt, must be in directory of the file
# database name is the database you're working with - run psql -h 34.125.112.255 -p 5433 -U postgres -d MathZoosTest to check database
# psycopg2 extracts data from sql
# can usually run just outside of the class, but if more complicated can create separate file to run
# if __name__ == "__main__" is imp since it defines code that'll only run when script is executed directly and not when it's imported as a module into another script
