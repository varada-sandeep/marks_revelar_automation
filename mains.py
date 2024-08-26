from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tkinter import Tk, simpledialog
from selenium.webdriver.common.window import WindowTypes
from tkinter import messagebox
import time
import tkinter as tk
import json


class Marks:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)
        url = "http://results.veltech.edu.in/Stulogin/"
        self.driver.get(url=url)
        self.login_pa()

    def login_pa(self):

        try:
            self.get_input()
            self.username = self.driver.find_element(By.CSS_SELECTOR, "#txtUserName")
            self.username.clear()
            self.username.send_keys(f"VTU{self.user_input}")
            self.txtPassword = self.driver.find_element(By.NAME, "txtPassword")
            self.txtPassword.send_keys(f"VTU{self.user_input}")

            time.sleep(1)
            self.login = self.driver.find_element(By.NAME, "LoginButton")
            self.login.click()
            time.sleep(1)
            self.Results = self.driver.find_element(By.LINK_TEXT, "Results")
            self.Results.click()

        except:
            self.error_show(2)

        anchor_script = """
            var anchor = document.querySelector('a[href="https://www.google.com"]');
            if (anchor) {
                anchor.click();
            } else {
                throw 'Anchor element not found';
            }
            """
        time.sleep(1)
        self.RegularResults = self.driver.find_element(
            By.XPATH, '//*[@id="nav"]/li[5]/ul/li[1]/a'
        )
        self.RegularResults.click()
        time.sleep(1)
        self.semester = {
            "1": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[1]',
            "2": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[2]',
            "3": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[3]',
            "4": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[4]',
            "5": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[5]',
            "6": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[6]',
            "7": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[7]',
            "8": '//*[@id="ContentPlaceHolder1_ddlSemester"]/option[8]',
        }
        find_ot = messagebox.askokcancel("To find","If you want to know gpa for one semester press 'ok'\n if cgpa press cancel ")
        if find_ot:
            self.sub_cred()

        else:

            self.cgpa_finder()

    def get_input(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.user_input = simpledialog.askstring(
            "Credentials", "Enter your VTU.no without with VTU"
        )

        self.root.destroy()

    def get_sem(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.user_input_sem = simpledialog.askstring(
            "Semester", "Enter the sem you want to know result(just the value)"
        )
        self.user_input_sem = str(self.user_input_sem)

        self.root.destroy()

    def sub_cred(self):
        self.get_sem()
        try:
            if self.user_input_sem is not None:
                self.sem = self.driver.find_element(
                    By.XPATH, self.semester[self.user_input_sem]
                )
            else:
                pass
        except:
            self.error_show(0)
        time.sleep(1)
        self.sem.click()

        self.table = self.driver.find_elements(By.CSS_SELECTOR, ".gridRowStyle")
        self.table2 = self.driver.find_elements(
            By.CSS_SELECTOR, ".gridAlternatingRowStyle"
        )
        if self.table == []:
            self.error_show(1)
        crdits_earned_per_subject = {}
        with open("marks_revelar_automation\\sub_credit.json", "r") as fp:
            r = fp.read()
            jl = json.loads(r)
            for i in self.table:
                n = i.text
                n = n.split()
                self.sub = " ".join(n[3:-2])
                if n[-1] == "Declared":
                    continue
                crdits_earned_per_subject[self.sub] = n[-2]
                if self.sub in jl:
                    continue
                else:
                    data = {self.sub: self.credit_finder()}
                jl.update(data)
            for i in self.table2:
                n = i.text
                n = n.split()
                self.sub = " ".join(n[3:-2])
                if n[-1] == "Declared":
                    continue
                crdits_earned_per_subject[self.sub] = n[-2]
                if self.sub in jl:
                    continue
                else:
                    data = {self.sub: self.credit_finder()}
                jl.update(data)
        with open("marks_revelar_automation\\sub_credit.json", "w") as fp:
            json.dump(jl, fp, indent=4)
        if crdits_earned_per_subject == {}:
            messagebox.showinfo(message="result not yet declared")
            self.sub_cred()
        else:
            gpa=self.result_calculator(crdits_earned_per_subject)
            messagebox.showinfo("GPA", f"{gpa}")
        logout = self.driver.find_element(By.XPATH, '//*[@id="LinkButton1"]')
        logout.click()
        self.driver.quit()

    def cgpa_finder(self):
        crdits_earned_per_subject = {}
        for i in self.semester.values():
            sem = self.driver.find_element(By.XPATH, i)
            time.sleep(1)
            sem.click()
            table = self.driver.find_elements(By.CSS_SELECTOR, ".gridRowStyle")
            table2 = self.driver.find_elements(
            By.CSS_SELECTOR, ".gridAlternatingRowStyle"
            )

            with open("marks_revelar_automation\\sub_credit.json", "r") as fp:
                r = fp.read()
                jl = json.loads(r)
                for i in table:
                    print(i)
                    n = i.text
                    n = n.split()
                    self.sub = " ".join(n[3:-2])
                    if n[-1] == "Declared":
                        continue
                    crdits_earned_per_subject[self.sub] = n[-2]
                    if self.sub in jl:
                        continue
                    else:
                        data = {self.sub: self.credit_finder()}
                    jl.update(data)
                for i in table2:
                    print(i)
                    n = i.text
                    n = n.split()
                    self.sub = " ".join(n[3:-2])
                    if n[-1] == "Declared":
                        continue
                    crdits_earned_per_subject[self.sub] = n[-2]
                    if self.sub in jl:
                        continue
                    else:
                        data = {self.sub: self.credit_finder()}
                    jl.update(data)
            with open("marks_revelar_automation\\sub_credit.json", "w") as fp:
                json.dump(jl, fp, indent=4)
        gpa = self.result_calculator(crdits_earned_per_subject)
        messagebox.showinfo("CGPA", f"{gpa}")
        logout = self.driver.find_element(By.XPATH, '//*[@id="LinkButton1"]')
        logout.click()
        self.driver.quit()

    def credit_finder(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.user_input_credd = simpledialog.askstring(
            "Asking credit", f"Enter the credits for {self.sub}"
        )

        self.root.destroy()
        return self.user_input_credd

    def result_calculator(self, lis):
        # self.driver.execute_script("window.open(" ");")
        # results = self.driver.window_handles[0]
        # gpa_calculator = self.driver.window_handles[1]
        # self.driver.switch_to.window(gpa_calculator)
        # self.driver.get("http://saikumarpoguweb.epizy.com/index.html?i=1")
        with open("marks_revelar_automation\\sub_credit.json", "r") as fp:
            r = json.loads(fp.read())

            creds = 0
            sum = 0
            grade_creds = {"S": 10, "A": 9, "B": 8, "C": 7, "D": 6}
            for i, j in lis.items():
                creds += int(r[i])
                sum += int(r[i]) * grade_creds[j]
            gpa = sum / creds

            return gpa
            # messagebox.showinfo("GPA", f"{gpa}")

    def error_show(self, err_sg):
        errors = ["Enter a valid sem number", "NO records found","enter a valid vtu number"]
        messagebox.showerror(title=None, message=errors[err_sg])
        if err_sg == 0 or err_sg == 1:
            self.sub_cred()
        elif err_sg == 2:
            self.login_pa()


t = Marks()
