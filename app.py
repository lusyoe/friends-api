from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# 加载环境变量
load_dotenv()

db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'blog')
}

@app.route('/api/sites')
def get_sites():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 查询所有激活站点
        cursor.execute("""
            SELECT id, name, logo, description, url, last_fetched_at
            FROM friend_links
            WHERE is_active = 1
        """)
        sites = cursor.fetchall()

        sites_with_articles = []
        for site in sites:
            # 查询最新一篇文章
            cursor.execute("""
                SELECT created_at FROM friend_rss_articles
                WHERE friend_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (site['id'],))
            latest_article = cursor.fetchone()
            if not latest_article or not latest_article['created_at']:
                continue
            # 判断最新文章是否在半年内
            if latest_article['created_at'] < (datetime.datetime.now() - datetime.timedelta(days=180)):
                continue

            # 查询最近半年内的文章，最多3篇
            cursor.execute("""
                SELECT title, link, created_at
                FROM friend_rss_articles
                WHERE friend_id = %s AND created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                ORDER BY created_at DESC
                LIMIT 3
            """, (site['id'],))
            articles = cursor.fetchall()

            # 如果不足3篇，再查更早的文章补足
            if len(articles) < 3:
                cursor.execute("""
                    SELECT title, link, created_at
                    FROM friend_rss_articles
                    WHERE friend_id = %s AND created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH)
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (site['id'], 3 - len(articles)))
                old_articles = cursor.fetchall()
                articles.extend(old_articles)

            # 格式化 created_at 字段
            for article in articles:
                if article['created_at']:
                    article['created_at'] = article['created_at'].strftime('%Y-%m-%d')
            if articles:
                site['articles'] = articles
                site['latest_article_time'] = articles[0]['created_at']
                sites_with_articles.append(site)
        # 按最新文章时间降序排序
        sites_with_articles.sort(key=lambda x: x['latest_article_time'], reverse=True)
        # 移除临时字段
        for site in sites_with_articles:
            site.pop('latest_article_time', None)
        cursor.close()
        conn.close()
        return jsonify(sites_with_articles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
