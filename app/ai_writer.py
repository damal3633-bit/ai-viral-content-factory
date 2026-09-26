def make_content(trend, language):
    topic = trend["title"]

    if language == "bn":
        title = f"{topic} — ১ মিনিটে জেনে নিন"

        hook = f"এই মুহূর্তে আলোচনায় রয়েছে: {topic}"

        body = (
            f"এই বিষয়টি নিয়ে এখন অনেক আলোচনা হচ্ছে। "
            f"মূল বিষয়টি হলো {topic}। "
            "ভিডিওটি প্রকাশের আগে মূল উৎস থেকে তথ্য যাচাই করে নিন।"
        )

        cta = "আরও এমন তথ্যের জন্য ফলো করুন।"

        hashtags = "#বাংলা #ট্রেন্ডিং #নিউজ #শর্টস"

    else:
        title = f"{topic} — 1 Minute Mein Janiye"

        hook = f"Abhi charcha mein hai: {topic}"

        body = (
            f"Is topic ko lekar abhi kaafi charcha ho rahi hai. "
            f"Main point hai: {topic}. "
            "Video publish karne se pehle original source se facts verify karein."
        )

        cta = "Aisi hi useful updates ke liye follow karein."

        hashtags = "#Hindi #Trending #News #Shorts"

    script = f"{hook}\n\n{body}\n\n{cta}"

    return {
        "language": language,
        "source_topic": topic,
        "source_url": trend["url"],
        "title": title[:95],
        "description": script + "\n\n" + hashtags,
        "hashtags": hashtags,
        "script": script
    }
