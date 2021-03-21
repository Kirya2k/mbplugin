import pytest
import conftest
import pyppeteeradd as pa  # pylint: disable=import-error
import sipnet2  # pylint: disable=import-error

# Игнорирование RuntimeWarning пришлось включить из-за того что pytest думает что нужен await в 
# self.browser.on("disconnected", self.disconnected_worker)
# и ругается - RuntimeWarning: coroutine ..... was never awaited
@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.slow
def test_sipnet2_logon_selectors():
    print(f'{sipnet2.login_url=}')
    self = pa.balance_over_puppeteer('test', 'test', 'test', login_url=sipnet2.login_url, user_selectors=sipnet2.user_selectors)
    self.main('check_logon')
