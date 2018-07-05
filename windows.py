import argparse
import getpass
import csv
import os
import random
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class EmailLoader:
    all_emails = []

    def __init__(self, filename):
        file_path = os.path.dirname(os.path.realpath(__file__)) + '\\' + filename
        print(file_path)
        if not os.path.isfile(file_path):
            sys.exit('File does not exist: ' + filename)

        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for email in csv_reader:
                self.all_emails.append(email[0])

        if len(self.all_emails) < 1:
            sys.exit('There are no emails in your supplied file')
        else:
            print('Loaded ' + str(len(self.all_emails)) + ' emails from ' + filename)

class Browser:
    delay = 3

    def __init__(self):
        chromedriver = os.path.dirname(os.path.realpath(__file__)) + '\\chromedriver'
        self.browser = webdriver.Chrome(chromedriver)

    def navigate(self, url, wait_for, error):
        try:
            print('Navigating to: ' + url)
            self.browser.get(url)
            element_present = expected_conditions.presence_of_element_located(
                (By.ID, wait_for))
            WebDriverWait(self.browser, self.delay).until(element_present)
        except TimeoutException:
            sys.exit(error)

    def enter_login_details(self, email, password):
        try:
            print('Entering login details')
            email_field = self.browser.find_element_by_id('email')
            pass_field = self.browser.find_element_by_id('pass')
            email_field.send_keys(email)
            pass_field.send_keys(password)
            pass_field.submit()
            element_present = expected_conditions.presence_of_element_located(
                (By.ID, 'userNavigationLabel'))
            WebDriverWait(self.browser, self.delay).until(element_present)
        except TimeoutException:
            sys.exit('Login with your credentials unsuccessful')

    def import_members(self, emails):
        print('Attempting to import email addresses')
        input_xpath = "//input[@placeholder='Enter name or email address...']"
        # input_xpath = "//input[@placeholder='Ingresa un nombre o correo electrónico...']"
        add_members_field = self.browser.find_element_by_xpath(input_xpath)
        for email in emails:
            add_members_field.send_keys(email)
            add_members_field.send_keys(Keys.RETURN)
            time.sleep(random.randint(1, self.delay))

    @staticmethod
    def _get_base_character(c):
        desc = unicodedata.name(unicode(c))
        cutoff = desc.find(' WITH ')
        if cutoff != -1:
            desc = desc[:cutoff]
        return unicodedata.lookup(desc)



def main():
    parser = argparse.ArgumentParser(description='This tool lets you invite people in bulk to your Facebook group')
    parser.add_argument('-e','--email', help='Your personal Facebook account email', required=True)
    parser.add_argument('-p','--password', help='Your personal Facebook password', required=True)    
    parser.add_argument('-g','--group', help='The Facebook group number', required=True)
    parser.add_argument('-f','--file', help='The csv file to load email addresses from', default='emails.csv')
    args = vars(parser.parse_args())

    email_loader = EmailLoader(filename=args['file'])
    browser = Browser()
    browser.navigate(
        url='https://www.facebook.com',
        wait_for='facebook',
        error='Unable to load the Facebook website'
    )
    browser.enter_login_details(email=args['email'], password=args['password'])
    browser.navigate(
        url='https://www.facebook.com/groups/' + args['group'],
        wait_for='pagelet_group_',
        error='Couldn\'t navigate to the group\'s members page'
    )
    browser.import_members(emails=email_loader.all_emails)
    print(str(len(email_loader.all_emails)) + ' email addresses successfully imported')

    

if __name__ == '__main__':
    main()
