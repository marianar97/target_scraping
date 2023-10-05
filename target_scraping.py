from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from collections import defaultdict
import pandas as pd


driver = webdriver.Chrome()

def get_categories_link():
    path = "https://www.target.com/c/shop-all-categories/-/N-5xsxf?prehydrateClick=true"
    driver.get(path)
    #wait for categories to exist
    categories = WebDriverWait(driver,50).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="pageBodyContainer"]/div/div[1]/div/div[14]'))
            )
    # # get the categories list
    categories_ls = categories.find_elements(By.CLASS_NAME, "cQxfob")
    links = []
    # time.sleep(1)
    for category in categories_ls[1::]:
        cat = category.find_elements(By.TAG_NAME, 'a')
        links.append(cat[0].get_attribute('href'))

    return links

def get_subcategories_link(link):
    driver.get(link)
    subs = WebDriverWait(driver,50).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jUzyfh"))
            )
    subs_list = subs.find_elements(By.TAG_NAME, 'li')

    href_subcat = []
    for item in subs_list:
        h = item.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
        sub_cat = item.find_elements(By.TAG_NAME, 'span')
        href_subcat.append((h, sub_cat[0].text))
    return href_subcat
    # return [item.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href') for item in subs_list]

def get_data(path, sub_category):
    #Fresh Dips
    print(sub_category)
    # if sub_category == 'Fresh Dips' or sub_category == 'Salsas & Hummus':
    #     print(path)
    print(path)
    if ',' in sub_category:
        sub_category = sub_category.split(",")
        sub_category = sub_category[0]

    driver.get(path)

    data = defaultdict(list)

    try:
        main = WebDriverWait(driver,50).until(
            EC.presence_of_element_located((By.CLASS_NAME, "kmNUvV"))
        )

        articles = main.find_elements(By.CLASS_NAME, "dOpyUp")

        for article in articles:
            art = []
            title = article.find_elements(By.CLASS_NAME, "iZqUcy")
            if not title:
                continue
            else:
                # art.append(title[0].text.strip())
                t = title[0].text.strip()

            # find price
            price = article.find_elements(By.CLASS_NAME, "kKRufV")
            price = price[0].text
            idx = price.find("$")

            end = -1
            for j, letter in enumerate(price[idx+1:]):
                if not letter.isnumeric() and letter != ".":
                    end = j
                    break
            if end <= 0:
                continue

            price = price[idx+1:end+1]

            try:
                art.append(float(price))
            except:
                print(f"Error: price'{price} cannot be converted to float'")
                print(price)
                continue

            art.append(sub_category)
            art.append(0)
            if len(art) > 3:
                print(art)
            data[t] = tuple(art)
            print(t, data[t])

    finally:
        # time.sleep(1)
        return data

def write_to_file(data):
    f = open('prices2.csv', 'w')

    f.write('name, price, category, quantity\n')
    for key, item in data.items():
        key = key.replace(",", "")
        f.write(key + "," + str(item[0]) + "," + str(item[1]) + "," + str(item[2]) + "\n")

    f.close()

if __name__ == "__main__":
    categories_links = get_categories_link()
    links_subcat = []
    for link in categories_links:
        links_subcat.extend(get_subcategories_link(link))

    links_subcat = links_subcat[2::]
    all_data = {}
    # i = 0
    for path, sub_category in links_subcat:
        # print(i)
        all_data.update(get_data(path, sub_category))
        # i+=1
        # if i == 1:
        #     break

    print("\n"*5)
    print("HERE")
    print(all_data)
    write_to_file(all_data)

