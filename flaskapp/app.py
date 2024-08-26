from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])  # type: ignore
def submit():
    user_input = request.form.get("user_input")
    action_type = request.form.get("action_type")

    if not user_input:
        return jsonify(success=False, message="Enter a valid VTU number")

    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        url = "http://results.veltech.edu.in/Stulogin/"
        driver.get(url=url)

        username = driver.find_element(By.CSS_SELECTOR, "#txtUserName")
        username.clear()
        username.send_keys(f"VTU{user_input}")
        txtPassword = driver.find_element(By.NAME, "txtPassword")
        txtPassword.send_keys(f"VTU{user_input}")

        time.sleep(1)
        login = driver.find_element(By.NAME, "LoginButton")
        login.click()
        time.sleep(1)
        Results = driver.find_element(By.XPATH, '//*[@id="nav"]/li[5]/a')
        Results.click()
        time.sleep(2)
        RegularResults = driver.find_element(
            By.XPATH, '//*[@id="nav"]/li[5]/ul/li[1]/a'
        )
        RegularResults.click()
        time.sleep(1)

        if action_type == "gpa":
            semester = request.form.get("semester")
            sem_xpath = f'//*[@id="ContentPlaceHolder1_ddlSemester"]/option[{semester}]'
            sem = driver.find_element(By.XPATH, sem_xpath)
            sem.click()

            table = driver.find_elements(By.CSS_SELECTOR, ".gridRowStyle")
            table2 = driver.find_elements(By.CSS_SELECTOR, ".gridAlternatingRowStyle")

            if not table and not table2:
                return jsonify(success=False, message="No records found")

            crdits_earned_per_subject = {}
            with open("marks_revelar_automation\\flaskapp\\sub_credit.json", "r") as fp:
                r = fp.read()
                jl = json.loads(r)
                for i in table:
                    n = i.text.split()
                    sub = " ".join(n[3:-2])
                    if n[-1] == "Declared":
                        continue
                    crdits_earned_per_subject[sub] = n[-2]
                    if sub not in jl:
                        return jsonify(
                            success=False,
                            message=f"Enter credits for {sub}",
                            subject=sub,
                        )
                    else:
                        jl.update({sub: jl[sub]})
                for i in table2:
                    n = i.text.split()
                    sub = " ".join(n[3:-2])
                    if n[-1] == "Declared":
                        continue
                    crdits_earned_per_subject[sub] = n[-2]
                    if sub not in jl:
                        return jsonify(
                            success=False,
                            message=f"Enter credits for {sub}",
                            subject=sub,
                        )
                    else:
                        jl.update({sub: jl[sub]})

            with open("marks_revelar_automation\\flaskapp\\sub_credit.json", "w") as fp:
                json.dump(jl, fp, indent=4)

            gpa = result_calculator(crdits_earned_per_subject)
            return jsonify(success=True, message=f"GPA: {gpa}")

        elif action_type == "cgpa":
            crdits_earned_per_subject = {}
            semester_xpath = {
                "1": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[1]',
                "2": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[2]',
                "3": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[3]',
                "4": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[4]',
                "5": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[5]',
                "6": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[6]',
                "7": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[7]',
                "8": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[8]',
            }
            for sem_xpath in semester_xpath.values():
                sem = driver.find_element(By.XPATH, sem_xpath)
                time.sleep(1)
                sem.click()
                table = driver.find_elements(By.CSS_SELECTOR, ".gridRowStyle")
                table2 = driver.find_elements(
                    By.CSS_SELECTOR, ".gridAlternatingRowStyle"
                )

                with open(
                    "marks_revelar_automation\\flaskapp\\sub_credit.json", "r"
                ) as fp:
                    r = fp.read()
                    jl = json.loads(r)
                    for i in table:
                        n = i.text.split()
                        sub = " ".join(n[3:-2])
                        if n[-1] == "Declared":
                            continue
                        crdits_earned_per_subject[sub] = n[-2]
                        if sub not in jl:
                            return jsonify(
                                success=False,
                                message=f"Enter credits for {sub}",
                                subject=sub,
                            )
                        else:
                            jl.update({sub: jl[sub]})
                    for i in table2:
                        n = i.text.split()
                        sub = " ".join(n[3:-2])
                        if n[-1] == "Declared":
                            continue
                        crdits_earned_per_subject[sub] = n[-2]
                        if sub not in jl:
                            return jsonify(
                                success=False,
                                message=f"Enter credits for {sub}",
                                subject=sub,
                            )
                        else:
                            jl.update({sub: jl[sub]})

            with open("marks_revelar_automation\\flaskapp\\sub_credit.json", "w") as fp:
                json.dump(jl, fp, indent=4)

            gpa = result_calculator(crdits_earned_per_subject)
            return jsonify(success=True, message=f"CGPA: {gpa}")

    except Exception as e:
        return jsonify(success=False, message=str(e))

    finally:
        logout = driver.find_element(By.XPATH, '//*[@id="LinkButton1"]')
        logout.click()
        driver.quit()


@app.route("/submit_credits", methods=["POST"])
def submit_credits():
    subject = request.form.get("subject")
    credits = request.form.get("credits")

    if not subject or not credits:
        return jsonify(success=False, message="Missing subject or credits")

    try:
        with open("marks_revelar_automation\\flaskapp\\sub_credit.json", "r") as fp:
            jl = json.load(fp)

        jl[subject] = credits

        with open("marks_revelar_automation\\flaskapp\\sub_credit.json", "w") as fp:
            json.dump(jl, fp, indent=4)

        return jsonify(success=True, message="Credits updated successfully")

    except Exception as e:
        return jsonify(success=False, message=str(e))


def result_calculator(crdits_earned_per_subject):
    with open("marks_revelar_automation\\flaskapp\\sub_credit.json", "r") as fp:
        r = json.loads(fp.read())

        creds = 0
        total_points = 0
        grade_points = {"S": 10, "A": 9, "B": 8, "C": 7, "D": 6}

        for subject, grade in crdits_earned_per_subject.items():
            if subject in r:
                creds += int(r[subject])
                total_points += int(r[subject]) * grade_points.get(grade, 0)

        gpa = total_points / creds if creds != 0 else 0
        return gpa


if __name__ == "__main__":
    app.run(debug=True)
