from whale import (
    santiment_fetcher,
    google_trends,
    cryptopanic_fetcher,
    fetch_fear_and_greed,
    reddit_crawler
)

def grab_analysis():
    print("📈 Running daily analysis fetchers...\n")

    cryptopanic_fetcher.main()
    santiment_fetcher.main()
    google_trends.main()
    fetch_fear_and_greed.main()
    reddit_crawler.main()
    

    print("\n✅ Daily data fetch complete. Ready for analysis.\n")