import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 配置信息
phone = "15986373998"
pwd = "Asdfghjkl456"
url1 = "https://onlineweb.zhihuishu.com/"
url2 = "https://hike.zhihuishu.com/aidedteaching/sourceLearning/sourceLearning?courseId=10914055&fileId=22409575"

# 初始化浏览器
def init_browser():
    return webdriver.Chrome()

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

# 格式化时间
def format_time(seconds):
    if seconds is None:
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

# 查找未完成视频
def find_unfinished_videos(browser):
    icon_video_elements = browser.find_elements(By.CSS_SELECTOR, 'i.icon-video')
    icon_finish_elements = browser.find_elements(By.CSS_SELECTOR, 'i.icon-finish')
    print(f"找到的视频图标数量: {len(icon_video_elements)}")
    print(f"找到的完成图标数量: {len(icon_finish_elements)}")

    icon_video_parents = [video.find_element(By.XPATH, './..') for video in icon_video_elements]
    icon_finish_parents = [finish.find_element(By.XPATH, './../..') for finish in icon_finish_elements]

    print(f"未完成视频图标父元素数量: {len(icon_video_parents)}")
    print(f"已完成视频图标父元素数量: {len(icon_finish_parents)}")

    icon_unfinish_parents = [parent for parent in icon_video_parents if parent not in icon_finish_parents]
    print(f"筛选出的未完成视频数量: {len(icon_unfinish_parents)}")

    return icon_unfinish_parents

# 播放视频并等待结束
def play_video_and_wait(browser, video_player, parent_name):
    video_player = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "video"))
    )
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

# 主函数
def main():
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

            play_video_and_wait(browser, video_player, parent_name)

    except Exception as e:
        print(f"错误: {e}")
    finally:
        browser.quit()

if __name__ == "__main__":
    main()