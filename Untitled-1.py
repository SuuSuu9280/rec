import requests
import re
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def get_google_news_links(search_term=None, num_pages=1):
    """
    Googleニュースから記事リンクを取得
    """
    base_url = "https://news.google.com/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    google_links = []
    
    for page in range(num_pages):
        params = {}
        if search_term:
            params['q'] = search_term
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Googleニュースのリンクを抽出（実際の構造に応じて調整が必要）
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if href and '/articles/' in href:
                    full_url = urljoin('https://news.google.com', href)
                    google_links.append(full_url)
            
            time.sleep(1)  # リクエスト間隔を空ける
            
        except requests.RequestException as e:
            print(f"Error fetching page {page + 1}: {e}")
            continue
    
    return google_links

def get_redirect_url(google_news_url):
    """
    GoogleニュースのURLをリダイレクト先URLに変換
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # allow_redirects=Falseでリダイレクトを手動で処理
        response = requests.get(google_news_url, headers=headers, allow_redirects=False)
        
        if response.status_code in [301, 302, 303, 307, 308]:
            # リダイレクト先URLを取得
            redirect_url = response.headers.get('Location')
            if redirect_url:
                return redirect_url
        
        # リダイレクトがない場合は元のURLを返す
        return google_news_url
        
    except requests.RequestException as e:
        print(f"Error processing {google_news_url}: {e}")
        return None

def extract_final_url_from_google_redirect(redirect_url):
    """
    Google経由のリダイレクトURL（/url?q=...形式）から最終URLを抽出
    """
    if '/url?q=' in redirect_url:
        # URLパラメータから実際のURLを抽出
        match = re.search(r'[?&]q=([^&]+)', redirect_url)
        if match:
            from urllib.parse import unquote
            return unquote(match.group(1))
    
    return redirect_url

def process_google_news_urls(google_urls):
    """
    GoogleニュースURLのリストを処理してリダイレクト先URLを取得
    """
    results = []
    
    for i, url in enumerate(google_urls, 1):
        print(f"Processing {i}/{len(google_urls)}: {url}")
        
        redirect_url = get_redirect_url(url)
        
        if redirect_url:
            # Google経由のリダイレクトの場合、最終URLを抽出
            final_url = extract_final_url_from_google_redirect(redirect_url)
            
            results.append({
                'original': url,
                'redirect': redirect_url,
                'final': final_url
            })
        
        time.sleep(0.5)  # レート制限を避ける
    
    return results

def save_results_to_file(results, filename='google_news_redirects.txt'):
    """
    結果をファイルに保存
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Google News URL Redirects\n")
        f.write("=" * 50 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{i}. Original Google News URL:\n")
            f.write(f"   {result['original']}\n\n")
            f.write(f"   Redirect URL:\n")
            f.write(f"   {result['redirect']}\n\n")
            f.write(f"   Final URL:\n")
            f.write(f"   {result['final']}\n\n")
            f.write("-" * 50 + "\n\n")

def main():
    """
    メイン実行関数
    """
    print("Googleニュース リダイレクトURL取得ツール")
    print("=" * 40)
    
    # 方法1: 手動でURLを入力
    manual_urls = []
    print("\n1. 手動でURLを入力する場合:")
    print("GoogleニュースのURLを入力してください（終了するには空行を入力）:")
    
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        manual_urls.append(url)
    
    # 方法2: 検索キーワードで自動取得（実験的）
    search_urls = []
    search_term = input("\n2. 検索キーワードを入力（スキップするには空行）: ").strip()
    
    if search_term:
        print(f"'{search_term}'で検索中...")
        search_urls = get_google_news_links(search_term, num_pages=1)
        print(f"{len(search_urls)}個のURLを見つけました")
    
    all_urls = manual_urls + search_urls
    
    if not all_urls:
        print("処理するURLがありません。")
        return
    
    print(f"\n{len(all_urls)}個のURLを処理します...")
    results = process_google_news_urls(all_urls)
    
    # 結果を表示
    print("\n処理結果:")
    print("=" * 40)
    for i, result in enumerate(results, 1):
        print(f"{i}. 最終URL: {result['final']}")
    
    # ファイルに保存
    save_results_to_file(results)
    print(f"\n詳細結果を 'google_news_redirects.txt' に保存しました")

if __name__ == "__main__":
    main()