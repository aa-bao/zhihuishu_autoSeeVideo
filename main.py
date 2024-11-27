import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

phone = "15986373998"
pwd = "Asdfghjkl456"
url1 = "https://onlineweb.zhihuishu.com/"
url2 = "https://hike.zhihuishu.com/aidedteaching/sourceLearning/sourceLearning?courseId=10914055&fileId=22409575"

browser = webdriver.Chrome()
browser.get(url1)

# 登录验证，需要手动输入验证码
wait = WebDriverWait(browser, 10)
wait.until(EC.presence_of_element_located((By.ID, "lUsername"))).send_keys(phone)
browser.find_element(By.ID, "lPassword").send_keys(pwd)
browser.find_element(By.CLASS_NAME, "wall-sub-btn").click()

timeout = 60  # 设置超时时间为60秒
end_time = time.time() + timeout

while time.time() < end_time:
    try:
        if browser.find_element(By.ID, "cns-main-app"):
            browser.get(url2)
            break
    except:
        time.sleep(0.5)

def format_time(seconds):
    if seconds is None:
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

# def find_unfinished_videos():
#     # 查找所有符合条件的 div 元素
#     elements = browser.find_elements(By.CSS_SELECTOR, '.file-item')
#
#     # 获取 i.icon-video 和 i.icon-finish 标签及其父元素
#     icon_video_elements = []
#     icon_finish_elements = []
#
#     for el in elements:
#         icon_video_elements.extend(el.find_elements(By.CSS_SELECTOR, 'i.icon-video'))
#         icon_finish_elements.extend(el.find_elements(By.CSS_SELECTOR, 'i.icon-finish'))
#
#     icon_video_parents = [video.find_element(By.XPATH, './..') for video in icon_video_elements]
#     icon_finish_parents = [finish.find_element(By.XPATH, './../..') for finish in icon_finish_elements]
#     icon_unfinish_parents = [parent for parent in icon_video_parents if parent not in icon_finish_parents]
#
#     return icon_unfinish_parents
def find_unfinished_videos():
    # 通过图标查找所有符合条件的 div 元素
    icon_video_elements = browser.find_elements(By.CSS_SELECTOR, 'i.icon-video')
    icon_finish_elements = browser.find_elements(By.CSS_SELECTOR, 'i.icon-finish')
    print(f"找到的视频图标数量: {len(icon_video_elements)}")
    print(f"找到的完成图标数量: {len(icon_finish_elements)}")

    # 获取父级元素
    icon_video_parents = [video.find_element(By.XPATH, './..') for video in icon_video_elements]
    icon_finish_parents = [finish.find_element(By.XPATH, './../..') for finish in icon_finish_elements]

    print(f"未完成视频图标父元素数量: {len(icon_video_parents)}")
    print(f"已完成视频图标父元素数量: {len(icon_finish_parents)}")

    # 筛选未完成视频
    icon_unfinish_parents = [parent for parent in icon_video_parents if parent not in icon_finish_parents]
    print(f"筛选出的未完成视频数量: {len(icon_unfinish_parents)}")

    return icon_unfinish_parents

try:
    # 等待页面加载完
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "file-item"))
    )

    # icon_unfinish_parents = find_unfinished_videos()
    # print(find_unfinished_videos())
    #
    # if not icon_unfinish_parents:
    #     print("所有视频已播放完毕.")

    while True:
        print("开始查找未播放的视频")
        icon_unfinish_parents = find_unfinished_videos()
        print("未播放的视频数量为：", len(icon_unfinish_parents))

        for parent in icon_unfinish_parents:
            parent_name = parent.find_element(By.CLASS_NAME, "file-name").text
            print(f"父元素:\n{parent.get_attribute('outerHTML')}")
            parent.click()

            try:
                # 等待页面更新，直到视频元素出现
                video_player = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )

                # 使用 JavaScript 播放视频
                browser.execute_script("arguments[0].play();", video_player)
                # print(f"视频：{parent_name} 开始播放")

                video_duration = browser.execute_script("return arguments[0].duration;", video_player)
                print(f"视频总时长: {format_time(video_duration)}")

                # 检测视频是否刚开始播放，如果是，则记录开始时间
                current_time = browser.execute_script("return arguments[0].currentTime;", video_player)
                if current_time == 0:
                    start_time = time.time()
                else:
                    start_time = time.time() - current_time

                # 检测视频播放情况
                while True:
                    # 获取当前播放时间
                    current_time = browser.execute_script("return arguments[0].currentTime;", video_player)
                    elapsed_time = time.time() - start_time

                    print(f"当前时长: {format_time(current_time)}, 剩余时长: {format_time(video_duration - current_time)}")

                    if current_time >= video_duration:
                        print("视频播放完成.")
                        break

                    time.sleep(5)

            except TimeoutException:
                print("超时.")
                continue

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # 等待一段时间查看结果
    input("Press Enter to close the browser...")
    # 关闭浏览器
    browser.quit()