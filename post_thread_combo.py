"""
ワンストップ自動投稿スクリプト
1. 親ポスト（画像付き or テキスト）を投稿
2. 数秒待って、そのリプライに直アフィリリンク＋ミニサイトリンクを自動投稿
"""

import sys
import time
from post_to_threads import post_thread, load_env
import urllib.request
import urllib.parse
import json


def post_thread_with_image(text: str, image_url: str = None, reply_to_id: str = None) -> str:
    env = load_env()
    token = env.get("THREADS_ACCESS_TOKEN")
    user_id = env.get("THREADS_USER_ID")

    container_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    params = {
        "text": text,
        "access_token": token,
    }

    if image_url:
        params["media_type"] = "IMAGE"
        params["image_url"] = image_url
    else:
        params["media_type"] = "TEXT"

    if reply_to_id:
        params["reply_to_id"] = reply_to_id

    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(container_url, data=data, method="POST")

    with urllib.request.urlopen(req) as res:
        res_data = json.loads(res.read().decode("utf-8"))
        creation_id = res_data.get("id")

    print(f"📦 コンテナ作成完了 (ID: {creation_id})。公開処理中...")
    time.sleep(3)

    publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
    pub_data = urllib.parse.urlencode({"creation_id": creation_id, "access_token": token}).encode("utf-8")
    pub_req = urllib.request.Request(publish_url, data=pub_data, method="POST")

    with urllib.request.urlopen(pub_req) as pub_res:
        pub_res_data = json.loads(pub_res.read().decode("utf-8"))
        post_id = pub_res_data.get("id")

    return post_id


def post_full_thread_set(main_text: str, reply_link_url: str, item_title: str = "", image_url: str = None):
    """
    親ポスト（画像付きOK） ➔ 自動で返信に直リンクを投稿するセット実行関数
    """
    print("🚀 [1/2] 親ポストを投稿中...")
    parent_id = post_thread_with_image(main_text, image_url=image_url)
    print(f"🎉 親ポスト成功！ (ID: {parent_id})")

    print("⏳ 3秒待機してリプライを自動投稿します...")
    time.sleep(3)

    reply_text = f"▼ 使ってるのはコレです（詳細・在庫はこちら✨）\n{reply_link_url}\n\n他にも愛用アイテムはプロフのお部屋にまとめてます🌙\nhttps://yoru-room.vercel.app/"
    if item_title:
        reply_text = f"▼ 『{item_title}』の詳細はこちら（#PR）\n{reply_link_url}\n\n他にも愛用アイテムはプロフのお部屋にまとめてます🌙\nhttps://yoru-room.vercel.app/"

    print("🚀 [2/2] リプライ（直リンク）を自動投稿中...")
    reply_id = post_thread_with_image(reply_text, reply_to_id=parent_id)
    print(f"🎉 リプライ投稿も大成功！ (ID: {reply_id})")
    print(f"👉 スレッドURL: https://www.threads.net/@yoru_2521/post/{parent_id}")
    return parent_id, reply_id


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        main_t = sys.argv[1]
        link = sys.argv[2]
        img = sys.argv[3] if len(sys.argv) > 3 else None
        post_full_thread_set(main_t, link, image_url=img)
