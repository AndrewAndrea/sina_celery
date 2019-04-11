from tqdm import tqdm

from lxml import etree
from sina_celery.page_get.get_content import get_content, get_page_content


def parse_content():
    html = get_content()
    selector = etree.HTML(html)
    if selector.xpath("//input[@name='mp']") == []:
        page_num = 1
    else:
        page_num = (int)(selector.xpath(
            "//input[@name='mp']")[0].attrib["value"])
    print(page_num, '页数')
    for page in tqdm(range(1, page_num + 1), desc=u"进度"):
        html2 = get_page_content(page)
        selector2 = etree.HTML(html2)
        try:
            info = selector2.xpath("//div[@class='c']")
            is_empty = info[0].xpath("div/span[@class='ctt']")
            if is_empty:
                for i in range(0, len(info) - 2):
                    # print(info[i])
                    yield info[i]
        except AttributeError as e:
            # 更换cookie
            print('cookie过期' + str(e))
            return False