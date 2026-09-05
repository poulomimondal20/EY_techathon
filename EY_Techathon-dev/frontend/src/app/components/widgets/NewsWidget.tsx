import { Newspaper, ExternalLink, Clock, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

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

// Mock data for when API is unavailable
const MOCK_NEWS: NewsArticle[] = [
  {
    title: "FDA Approves New Alzheimer's Disease Treatment",
    description: "Revolutionary drug shows promise in slowing cognitive decline in early-stage patients.",
    url: "#",
    source: "Pharmaceutical Times",
    published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    image_url: null,
  },
  {
    title: "Breakthrough in Cancer Immunotherapy Research",
    description: "New combination therapy demonstrates 70% response rate in clinical trials.",
    url: "#",
    source: "Medical News Today",
    published_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    image_url: null,
  },
  {
    title: "Global Vaccine Distribution Reaches New Milestone",
    description: "Over 5 billion doses administered worldwide as pharmaceutical companies scale production.",
    url: "#",
    source: "Reuters Health",
    published_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
    image_url: null,
  },
];

export function NewsWidget() {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useMock, setUseMock] = useState(false);

  const fetchNews = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/news/cached`);
      if (!response.ok) {
        // Check if it's a server not running error
        throw new Error(`Server returned ${response.status}`);
      }
      
      const data: NewsResponse = await response.json();
      if (data.status === 'success' && data.articles && data.articles.length > 0) {
        setNews(data.articles.slice(0, 6)); // Show top 6
        setError(null);
        setUseMock(false);
      } else if (data.status.startsWith('error')) {
        // API key missing or other API error - use mock data
        setNews(MOCK_NEWS);
        setError('Using sample data. Set NEWS_API_KEY for live news.');
        setUseMock(true);
      } else {
        setNews(MOCK_NEWS);
        setError('No live news available. Showing sample data.');
        setUseMock(true);
      }
    } catch (err) {
      console.error('News fetch error:', err);
      // Use mock data as fallback
      setNews(MOCK_NEWS);
      setUseMock(true);
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Backend offline. Showing sample data.');
      } else {
        setError('API unavailable. Showing sample data.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
    // Refresh every 10 minutes
    const interval = setInterval(fetchNews, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h3 className="text-lg mb-4 flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-blue-400" />
          Latest Pharmaceutical News
        </h3>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h3 className="text-lg mb-4 flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-blue-400" />
          Latest Pharmaceutical News
          {useMock && (
            <span className="text-xs bg-yellow-400/20 text-yellow-400 px-2 py-0.5 rounded-full ml-2">
              Sample Data
            </span>
          )}
        </h3>
        <div className="bg-yellow-400/10 border border-yellow-400/30 rounded-lg p-3 mb-4">
          <p className="text-xs text-yellow-400">{error}</p>
        </div>
        {useMock && news.length > 0 && (
          <div className="space-y-3">
            {news.map((article, idx) => (
              <div
                key={idx}
                className="block bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 opacity-75"
              >
                <div className="flex gap-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-white mb-1 line-clamp-2">
                      {article.title}
                    </h4>
                    {article.description && (
                      <p className="text-xs text-gray-400 line-clamp-2 mb-2">
                        {article.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Newspaper className="w-3 h-3" />
                        {article.source}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDate(article.published_at)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-blue-400" />
          Latest Pharmaceutical News
          <span className="text-xs bg-blue-400/20 text-blue-400 px-2 py-0.5 rounded-full ml-2">
            Auto-updated
          </span>
        </h3>
        <button
          onClick={fetchNews}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {news.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">No news available</p>
        ) : (
          news.map((article, idx) => (
            <a
              key={idx}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 hover:border-blue-400/50 transition-all group"
            >
              <div className="flex gap-3">
                {article.image_url && (
                  <div className="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-[#0f1722]">
                    <img
                      src={article.image_url}
                      alt={article.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-white mb-1 line-clamp-2 group-hover:text-blue-400 transition-colors">
                    {article.title}
                  </h4>
                  {article.description && (
                    <p className="text-xs text-gray-400 line-clamp-2 mb-2">
                      {article.description}
                    </p>
                  )}
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Newspaper className="w-3 h-3" />
                      {article.source}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(article.published_at)}
                    </span>
                  </div>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors flex-shrink-0" />
              </div>
            </a>
          ))
        )}
      </div>
    </div>
  );
}
