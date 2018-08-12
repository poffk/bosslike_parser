from time import sleep

from InstagramAPI import InstagramAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

BOSSLIKE_URL = 'https://bosslike.ru'
TASK_HTML_HEIGHT = 137


class BosslikeParser:
    def __init__(self, source, task_type, solve_task):
        self.login = config.BOSSLIKE_LOGIN
        self.password = config.BOSSLIKE_PASSWORD
        self.source = source
        self.task_type = task_type
        self.solve_task = solve_task
        self.driver = webdriver.Firefox()

    def auth(self):
        self.driver.get(f'{BOSSLIKE_URL}/login/')
        username = self.driver.find_element_by_name('UserLogin[login]')
        password = self.driver.find_element_by_name('UserLogin[password]')

        username.send_keys(config.BOSSLIKE_LOGIN)
        password.send_keys(config.BOSSLIKE_PASSWORD)

        self.driver.find_element_by_name('submitLogin').click()

    def get_tasks(self):
        self.driver.get(f'{BOSSLIKE_URL}/tasks/{self.source}/{self.task_type}/')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'do')))
        return self.driver.find_elements_by_class_name('do')

    def scroll_to_next_task(self, task_number):
        self.driver.execute_script(f'window.scrollTo(0, {task_number*TASK_HTML_HEIGHT})')

    def process_tasks(self):
        tasks = self.get_tasks()
        for task_number, task in enumerate(tasks):
            sleep(2)
            task.click()

            if len(self.driver.window_handles) == 1:
                self.scroll_to_next_task(task_number)
                continue

            self.driver.switch_to.window(self.driver.window_handles[-1])
            # FIXME for another sources
            WebDriverWait(self.driver, 10).until(EC.url_contains(f'{self.source}'))

            self.solve_task(self.driver.current_url)

            self.driver.close()

            self.driver.switch_to.window(self.driver.window_handles[0])
            self.scroll_to_next_task(task_number)


def follow_instagram_by_username(url, sessions=[]):
    if not sessions:
        instagram = InstagramAPI(config.INSTAGRAM_LOGIN, config.INSTAGRAM_PASSWORD)
        instagram.login()
        sessions.append(instagram)

    session = sessions[0]

    username = url.split('/')[-2]
    session.searchUsername(username)
    user_id = session.LastJson["user"]["pk"]
    return session.follow(user_id)


if __name__ == '__main__':
    parser = BosslikeParser('instagram', 'subscribe', follow_instagram_by_username)
    parser.auth()

    while True:
        parser.process_tasks()
