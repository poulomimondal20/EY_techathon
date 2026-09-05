import { useEffect, useState, useCallback, useRef } from 'react';
import { X, TrendingUp, AlertCircle, CheckCircle, Newspaper } from 'lucide-react';

interface NewsArticle {
  title: string;
  description: string | null;
  url: string;
  source: string;
  published_at: string;
  image_url: string | null;
}

interface NewsResponse {
  status: string;
  total_results: number;
  articles: NewsArticle[];
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'news';
  message: string;
  timestamp: string;
  url?: string;
  source?: string;
}

const API_BASE_URL = 'http://localhost:8000';

// ============================================================
// NEWS FETCH & DISPLAY INTERVAL CONFIGURATION
// ============================================================
// Change these values to adjust how often news is fetched and displayed:
// - For testing: use 10000 (10 seconds)
// - For production: use 3600000 (1 hour)
// ============================================================
const NEWS_FETCH_INTERVAL_MS = 3600000; // 1 hour = 3600000ms | For 10 sec: use 10000
const NEWS_DISPLAY_INTERVAL_MS = 3600000; // 1 hour = 3600000ms | For 10 sec: use 10000
// ============================================================

export function NotificationSystem() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [currentNewsIndex, setCurrentNewsIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const lastFetchedIds = useRef<Set<string>>(new Set());

  // Fetch news from the API
  const fetchNews = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/news/medicine?page=1&page_size=20`);

      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }

      const data: NewsResponse = await response.json();
      console.log('News API response:', data);

      if (data.status === 'success' && data.articles.length > 0) {
        setNewsArticles(data.articles);

        // Show first article immediately if we have new articles
        const firstArticle = data.articles[0];
        const articleId = `${firstArticle.title}-${firstArticle.published_at}`;

        if (!lastFetchedIds.current.has(articleId)) {
          lastFetchedIds.current.add(articleId);
          const notification: Notification = {
            id: Date.now().toString(),
            type: 'news',
            message: firstArticle.title,
            timestamp: formatTimestamp(firstArticle.published_at),
            url: firstArticle.url,
            source: firstArticle.source,
          };
          setNotifications((prev) => [notification, ...prev].slice(0, 3));
          setCurrentNewsIndex(1);
        }
      } else {
        console.log('No articles returned or status not success:', data.status);
      }
    } catch (error) {
      console.error('Error fetching news:', error);
      // Show error notification
      const errorNotification: Notification = {
        id: Date.now().toString(),
        type: 'error',
        message: 'Failed to fetch latest news updates',
        timestamp: 'Just now',
      };
      setNotifications((prev) => [errorNotification, ...prev].slice(0, 3));
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Format timestamp to relative time
  const formatTimestamp = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      return `${diffDays}d ago`;
    } catch {
      return 'Recently';
    }
  };

  // Initial fetch and polling at configured interval
  useEffect(() => {
    // Fetch immediately on mount
    fetchNews();

    // Set up polling interval (configured via NEWS_FETCH_INTERVAL_MS constant above)
    // Current: 1 hour | Change to 10000 for 10 seconds
    const fetchInterval = setInterval(() => {
      fetchNews();
    }, NEWS_FETCH_INTERVAL_MS);

    return () => clearInterval(fetchInterval);
  }, [fetchNews]);

  // Cycle through fetched news articles
  useEffect(() => {
    if (newsArticles.length === 0) return;

    const cycleInterval = setInterval(() => {
      if (newsArticles.length > 0) {
        const article = newsArticles[currentNewsIndex % newsArticles.length];
        const articleId = `${article.title}-${article.published_at}`;

        // Only show if not recently shown
        if (!lastFetchedIds.current.has(articleId)) {
          lastFetchedIds.current.add(articleId);

          // Keep only last 20 IDs to prevent memory issues
          if (lastFetchedIds.current.size > 20) {
            const iterator = lastFetchedIds.current.values();
            lastFetchedIds.current.delete(iterator.next().value);
          }

          const notification: Notification = {
            id: Date.now().toString(),
            type: 'news',
            message: article.title,
            timestamp: formatTimestamp(article.published_at),
            url: article.url,
            source: article.source,
          };
          setNotifications((prev) => [notification, ...prev].slice(0, 3));
        }

        setCurrentNewsIndex((prev) => (prev + 1) % newsArticles.length);
      }
    }, NEWS_DISPLAY_INTERVAL_MS); // Display interval (configured via NEWS_DISPLAY_INTERVAL_MS constant above)
    // Current: 1 hour | Change to 10000 for 10 seconds

    return () => clearInterval(cycleInterval);
  }, [newsArticles, currentNewsIndex]);

  useEffect(() => {
    // Auto-remove notifications after 5 seconds
    const timers = notifications.map((notification) =>
      setTimeout(() => {
        removeNotification(notification.id);
      }, 5000)
    );

    return () => timers.forEach(clearTimeout);
  }, [notifications]);

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'warning':
        return <TrendingUp className="w-5 h-5 text-orange-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'news':
        return <Newspaper className="w-5 h-5 text-cyan-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-blue-400" />;
    }
  };

  const getBorderColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'border-green-400/30';
      case 'warning':
        return 'border-orange-400/30';
      case 'error':
        return 'border-red-400/30';
      case 'news':
        return 'border-cyan-400/30';
      default:
        return 'border-purple-400/30';
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (notification.url) {
      window.open(notification.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 space-y-3 max-w-md">
      {isLoading && notifications.length === 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-purple-400/30 rounded-xl p-4 shadow-2xl">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-400"></div>
            <p className="text-sm text-gray-300">Fetching latest news...</p>
          </div>
        </div>
      )}
      {notifications.map((notification) => (
        <div
          key={notification.id}
          onClick={() => handleNotificationClick(notification)}
          className={`bg-gradient-to-br from-[#0f1722] to-[#1a2533] border ${getBorderColor(
            notification.type
          )} rounded-xl p-4 shadow-2xl animate-slide-in-right ${notification.url ? 'cursor-pointer hover:bg-[#1a2533] transition-colors' : ''
            }`}
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5">{getIcon(notification.type)}</div>
            <div className="flex-1 min-w-0">
              <p className="text-sm mb-1 line-clamp-2">{notification.message}</p>
              <div className="flex items-center gap-2">
                <p className="text-xs text-gray-400">{notification.timestamp}</p>
                {notification.source && (
                  <>
                    <span className="text-gray-500">•</span>
                    <p className="text-xs text-cyan-400">{notification.source}</p>
                  </>
                )}
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeNotification(notification.id);
              }}
              className="text-gray-400 hover:text-white transition-colors flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}