import undetected_chromedriver as uc

def main():
    driver = uc.Chrome(use_subprocess=False)

    driver.get("https://csgocases.com")
    input("Press Enter to quit...")
    driver.quit()

if __name__ == "__main__":
    main()