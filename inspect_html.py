from bs4 import BeautifulSoup

def parse():
    with open('data/processed/bis_test_fetch.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Basic Details
    print("\n--- BASIC DETAILS ---")
    for el in soup.find_all(string=lambda t: t and 'Superseding IS' in t):
        # find the parent that contains the key and value
        parent = el.parent.parent
        print(f"Key/Value from parent: {' | '.join(parent.stripped_strings)}")

    # Try tables for amendments
    print("\n--- TABLES ---")
    for idx, t in enumerate(soup.find_all('table')):
        headers = [th.get_text(strip=True) for th in t.find_all('th')]
        if 'Amendment No.' in headers or 'IS/Amendment Number' in headers:
            print(f"Table {idx} Headers: {headers}")
            for row in t.find_all('tr')[1:]:
                print(f"  Row: {' | '.join([td.get_text(strip=True) for td in row.find_all('td')])}")

if __name__ == '__main__':
    parse()
