import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 初始化浏览器
def init_browser():
    return webdriver.Chrome()

# 读取配置信息
def read_config(file_path):
    config = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip().strip('"')
    return config

# 登录
def login(browser, phone, pwd, url1):
    browser.get(url1)
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, "lUsername"))).send_keys(phone)
    browser.find_element(By.ID, "lPassword").send_keys(pwd)
    browser.find_element(By.CLASS_NAME, "wall-sub-btn").click()

# 等待页面元素出现
def wait_for_element(browser, by, value, timeout=60):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            if browser.find_element(by, value):
                return
            time.sleep(0.5)
        except:
            pass
    raise TimeoutException("等待页面元素超时")


# 查找未完成视频
def find_unfinished_videos(browser):
    icon_video_elements = browser.find_elements(By.CSS_SELECTOR, 'i.icon-video')
    icon_finish_elements = browser.find_elements(By.CSS_SELECTOR, 'i.icon-finish')
    print(f"网页存在的视频总数: {len(icon_video_elements)}")
    print(f"已观看的视频数量: {len(icon_finish_elements)}")

    icon_video_parents = [video.find_element(By.XPATH, './..') for video in icon_video_elements]
    icon_finish_parents = [finish.find_element(By.XPATH, './../..') for finish in icon_finish_elements]

    icon_unfinish_parents = [parent for parent in icon_video_parents if parent not in icon_finish_parents]
    print(f"未观看完成的视频数量: {len(icon_unfinish_parents)}")

    return icon_unfinish_parents

# 播放视频并等待结束
def play_video_and_wait(browser, video_player, parent_name, mute_video):
    video_player = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "video"))
    )

    if mute_video:
        browser.execute_script("arguments[0].muted = true;", video_player)

    browser.execute_script("arguments[0].play();", video_player)
    print(f"视频：{parent_name} |开始播放")

    browser.execute_script("""
                var video = arguments[0];
                video.addEventListener('ended', function() {
                    console.log('视频播放完成');
                });
                """, video_player)

    try:
        WebDriverWait(browser, 3600).until(
            lambda x: x.execute_script("return arguments[0].ended;", video_player)
        )
        print(f"视频：{parent_name} |已播放完成。")
        # 播放完毕，刷新页面
        browser.refresh()
    except TimeoutException:
        print("视频播放超时。")

def check_config(phone, pwd, url1, url2):
    if not phone or not pwd or not url1 or not url2:
        print("配置文件不完整，请检查！")

# 主函数
def main():
    config = read_config('config.txt')
    phone = config.get('phone')
    pwd = config.get('pwd')
    url1 = config.get('url1')
    url2 = config.get('url2')
    mute_video = config.get('muteVideo', 'false').lower() == 'true'  # 默认静音


    if not phone or not pwd or not url1 or not url2:
        print("配置文件不完整，请检查！")
        return  # 退出程序

    browser = init_browser()
    try:
        login(browser, phone, pwd, url1)
        wait_for_element(browser, By.ID, "cns-main-app")
        # 进入课程
        browser.get(url2)

        while True:
            video_player = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'i.icon-video')))
            icon_unfinish_parents = find_unfinished_videos(browser)
            print("未播放的视频数量为：", len(icon_unfinish_parents))

            if not icon_unfinish_parents:
                print("所有视频已播放完成，程序退出。")
                break

            parent = icon_unfinish_parents[0]
            parent_name = parent.find_element(By.CLASS_NAME, "file-name").text
            parent.click()

            play_video_and_wait(browser, video_player, parent_name, mute_video)

    except Exception as e:
        print(f"错误: {e}")
    finally:
        browser.quit()

if __name__ == "__main__":
    main()