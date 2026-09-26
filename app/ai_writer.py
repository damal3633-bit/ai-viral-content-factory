def make_content(trend, language):
    topic = trend["title"]
    source_url = trend.get("url", "")

    if language == "bn":
        title = f"{topic} — ১ মিনিটে জেনে নিন"

        hook = f"🚨 এখন আলোচনায়: {topic}"

        body = (
            f"এই বিষয়টি নিয়ে বর্তমানে আলোচনা হচ্ছে। "
            f"মূল বিষয় হলো: {topic}। "
            "তথ্য প্রকাশের আগে মূল উৎস যাচাই করা গুরুত্বপূর্ণ।"
        )

        cta = "এমন আরও আপডেট পেতে ফলো করুন।"

        hashtags = "#বাংলা #ট্রেন্ডিং #নিউজ #শর্টস"

    else:
        title = f"{topic} — 1 Minute Mein Janiye"

        hook = f"🚨 Abhi charcha mein: {topic}"

        body = (
            f"Is topic ko lekar abhi charcha ho rahi hai. "
            f"Main point hai: {topic}. "
            "Publish karne se pehle original source se information verify karein."
        )

        cta = "Aisi hi useful updates ke liye follow karein."

        hashtags = "#Hindi #Trending #News #Shorts"

    script = f"{hook}\n\n{body}\n\n{cta}"

    return {
        "language": language,
        "source_topic": topic,
        "source_url": source_url,
        "title": title[:95],
        "description": script + "\n\n" + hashtags,
        "hashtags": hashtags,
        "script": script,
    }
