import asyncio
from pyppeteer import launch
from time import sleep
import random

# use pyppeteer replace selenium + chromedriver.exe go login taobao
# source from : [淘宝爬虫之强行登录如何解决Selenium被检测到的问题](https://www.jianshu.com/p/4dd2737a3048)
class TB:
    def __init__(self):
        self.url_login = 'https://login.taobao.com/member/login.jhtml'
        self.username = '马云'
        self.password = 'mayun19640910'

    async def login(self):
        browser = await launch({'headless': False, 'args': ['--no-sandbox'], 'userDataDir': 'd:\\'})
        page = await browser.newPage() # 启动浏览器页面
        await page.setViewport(viewport={'width': 2000, 'height': 800})
        await page.setUserAgent('Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36')
        await page.goto(self.url_login)


        await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''') #以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
        await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
        await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

        # 切换用户名密码方式登录
        await page.evaluate('document.getElementById("J_Quick2Static").click()')

        # type选定页面元素，模拟输入用户名密码
        #await page.type('#TPL_username_1', self.username, {'delay': self.input_time_random() - 50})
        await page.type('#TPL_password_1', self.password, {'delay': self.input_time_random()})

        sleep(3)

        slider = await page.Jeval('#nocaptcha', 'node => node.style')

        if slider:
            print('需要滑块验证')
            await self.slider_verify(page=page)

        await page.keyboard.press('Enter')
        await page.waitFor(10)
        await page.waitForNavigation()

        try:
            global error 
            error = await page.Jeval('#J_Message > p', 'node => node.textContent')
        except Exception as e:
            # no element matching... express login success
            print('no element matching...')
            error = None
        finally:
            if error:
                print(error)
            else:
                # 获取登录成功cookie
                cookies = await page.cookies()
                for cookie in cookies:
                    str = '{0}={1};'
                    str = str.format(cookie.get('name'), cookie.get('value'))
                    print(str)

        await page.screenshot({
            'path': 'screenshot.png',
            'fullPage': True
        })

        sleep(20)
        await browser.close()

    async def slider_verify(self, page=None):
        print('开始滑块验证')
        try:
            await page.hover('#nc_1_n1z') # 不同场景的验证码模块能名字不同。
            await page.mouse.down()
            await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
            await page.mouse.up()
        except Exception as e:
            print('滑块失败')
            print(e)

    def input_time_random(self):
        return random.randint(100, 151)

if __name__ == '__main__':
    tb = TB()
    asyncio.get_event_loop().run_until_complete(tb.login())