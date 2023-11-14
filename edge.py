import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog, QLineEdit, QGridLayout
from msedge.selenium_tools import Edge, EdgeOptions
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle, islice
import random

class YouTubeViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.link_label = QLabel('Link videos:')
        self.link_input = QTextEdit(self)
        self.load_links_button = QPushButton('Load Links', self)

        self.proxy_label = QLabel('Proxy list (ip:port:protocol):')
        self.proxy_input = QTextEdit(self)
        self.load_proxies_button = QPushButton('Load Proxies', self)

        self.user_agent_label = QLabel('User-Agent list:')
        self.user_agent_input = QTextEdit(self)
        self.load_user_agents_button = QPushButton('Load User Agents', self)

        self.time_label = QLabel('Min Viewing time (seconds):')
        self.time_input = QLineEdit(self)

        self.max_time_label = QLabel('Max Viewing time (seconds):')
        self.max_time_input = QLineEdit(self)

        self.thread_label = QLabel('Number of threads:')
        self.thread_input = QLineEdit(self)

        self.view_button = QPushButton('Start Viewing', self)

        self.log_label = QLabel('Log:')
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)

        self.activation_label = QLabel('Activation Code:')
        self.activation_input = QLineEdit(self)
        self.activate_button = QPushButton('Activate', self)

        layout_upper = QGridLayout()
        layout_upper.addWidget(self.link_label, 0, 0)
        layout_upper.addWidget(self.link_input, 1, 0, 1, 2)
        layout_upper.addWidget(self.load_links_button, 2, 0)
        layout_upper.addWidget(self.proxy_label, 0, 2)
        layout_upper.addWidget(self.proxy_input, 1, 2, 1, 2)
        layout_upper.addWidget(self.load_proxies_button, 2, 2)
        layout_upper.addWidget(self.user_agent_label, 0, 4)
        layout_upper.addWidget(self.user_agent_input, 1, 4, 1, 2)
        layout_upper.addWidget(self.load_user_agents_button, 2, 4)

        layout_lower = QGridLayout()
        layout_lower.addWidget(self.time_label, 0, 0)
        layout_lower.addWidget(self.time_input, 0, 1)
        layout_lower.addWidget(self.max_time_label, 0, 2)
        layout_lower.addWidget(self.max_time_input, 0, 3)
        layout_lower.addWidget(self.thread_label, 1, 0)
        layout_lower.addWidget(self.thread_input, 1, 1)
        layout_lower.addWidget(self.view_button, 1, 2, 1, 2) 

        layout_right = QVBoxLayout()
        layout_right.addWidget(self.activation_label)
        layout_right.addWidget(self.activation_input)
        layout_right.addWidget(self.activate_button)

        layout = QVBoxLayout()
        layout.addLayout(layout_upper)
        layout.addLayout(layout_lower)
        layout.addLayout(layout_right)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        self.load_links_button.clicked.connect(self.load_links)
        self.load_proxies_button.clicked.connect(self.load_proxies)
        self.load_user_agents_button.clicked.connect(self.load_user_agents)
        self.view_button.clicked.connect(self.start_viewing)
        self.activate_button.clicked.connect(self.activate_license)

    def load_links(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Text files (*.txt)")
        if file_dialog.exec_():
            file_names = file_dialog.selectedFiles()
            links = []
            for file_name in file_names:
                with open(file_name, 'r') as file:
                    links.extend([line.strip() for line in file.readlines()])
            self.link_input.setText('\n'.join(links))

    def load_proxies(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Text files (*.txt)")
        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            with open(file_name, 'r') as file:
                proxies = [line.strip() for line in file.readlines()]
                self.proxy_input.setText('\n'.join(proxies))

    def load_user_agents(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Text files (*.txt)")
        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            with open(file_name, 'r') as file:
                user_agents = [line.strip() for line in file.readlines()]
                self.user_agent_input.setText('\n'.join(user_agents))

    def start_viewing(self):
        links = [link.strip() for link in self.link_input.toPlainText().split('\n') if link.strip()]
        proxies = [proxy.strip() for proxy in self.proxy_input.toPlainText().split('\n') if proxy.strip()]
        user_agents = [user_agent.strip() for user_agent in self.user_agent_input.toPlainText().split('\n') if user_agent.strip()]
        min_view_time = int(self.time_input.text())
        max_view_time = int(self.max_time_input.text())
        num_threads = int(self.thread_input.text())

        if not links or not proxies or not user_agents or not min_view_time or not max_view_time or not num_threads:
            self.log_output.append('Please enter valid values for links, proxies, user agents, min view time, max view time, and number of threads.')
            return

        self.log_output.clear()

        def view_video(link, proxy, user_agent):
            try:
                view_time = random.randint(min_view_time, max_view_time)
                self.log_output.append(f"Viewing {link} with proxy: {proxy}, user agent: {user_agent} for {view_time} seconds")

                if not self.check_proxy(proxy):
                    return

                edge_options = EdgeOptions()
                edge_options.add_argument(f"user-agent={user_agent}")
                edge_options.add_argument(f"--proxy-server={proxy}")

                driver = Edge(options=edge_options)

                autoplay_link = link + "?autoplay=1"

                driver.get(autoplay_link)
                time.sleep(5) 

                play_button = driver.find_element_by_class_name('ytp-large-play-button')
                play_button.click()

                mute_button = driver.find_element_by_class_name('ytp-mute-button')
                mute_button.click()

                time.sleep(view_time - 6) 

                if "YouTube" in driver.title:
                    self.log_output.append(f"Viewing {link} with proxy {proxy}, user agent {user_agent} succeeded.\n")
                else:
                    self.log_output.append(f"Viewing {link} with proxy {proxy}, user agent {user_agent} failed.\n")

                driver.quit()

            except Exception as e:
                self.log_output.append(f"Error with proxy {proxy}, user agent {user_agent} for link {link}: {str(e)}")

        proxy_groups = [list(g) for g in islice(cycle(proxies), num_threads)]

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for link in links:
                for proxy_group in proxy_groups:
                    for user_agent in user_agents:
                        executor.submit(view_video, link, proxy_group[0], user_agent)
                        if not proxy_group:
                            break

    def check_proxy(self, proxy):
        try:
            edge_options = EdgeOptions()
            edge_options.add_argument("--headless") 
            edge_options.add_argument(f"--proxy-server={proxy}")

            driver = Edge(options=edge_options)

            driver.set_page_load_timeout(30)

            try:
                driver.get("https://www.google.com/") 

                if "Google" in driver.title:
                    self.log_output.append(f"Proxy {proxy} is live.")
                    driver.quit()
                    return True
                else:
                    self.log_output.append(f"Proxy {proxy} is not live. Switching to the next proxy.")
                    driver.quit()
                    return False
            except Exception as e:
                self.log_output.append(f"Error checking proxy {proxy}: {str(e)}. Switching to the next proxy.")
                return False

        except Exception as e:
            self.log_output.append(f"Error checking proxy {proxy}: {str(e)}. Switching to the next proxy.")
            return False

    def activate_license(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = YouTubeViewer()
    viewer.show()
    sys.exit(app.exec_())
