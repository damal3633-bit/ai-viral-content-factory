from datetime import date


STORIES = [
    {
        "title": "Funny Boy-এর হারানো মোবাইল",
        "story_bn": (
            "Funny Boy তার মোবাইল খুঁজতে পুরো বাড়ি তোলপাড় করে ফেলল। "
            "সে বিছানার নিচে, টেবিলের ওপর আর ব্যাগের ভিতর খুঁজল। "
            "শেষে সে দেখল মোবাইলটা তার নিজের হাতেই ছিল!"
        ),
        "story_hi": (
            "Funny Boy apna mobile dhoondhte dhoondhte poore ghar mein "
            "pareshan ho gaya। Bed ke neeche, table aur bag sab jagah dekha। "
            "Aakhir mein pata chala mobile uske apne haath mein hi tha!"
        ),
    },
    {
        "title": "Funny Boy-এর উড়ন্ত ছাতা",
        "story_bn": (
            "বৃষ্টির দিনে Funny Boy নতুন ছাতা নিয়ে বাইরে গেল। "
            "হঠাৎ জোর বাতাসে ছাতাটা উড়ে গেল। "
            "Funny Boy ছাতার পিছনে দৌড়াতে দৌড়াতে নিজেই কাদায় পড়ে গেল!"
        ),
        "story_hi": (
            "Baarish ke din Funny Boy naya chhata lekar bahar gaya। "
            "Achanak tez hawa se chhata ud gaya। "
            "Funny Boy chhate ke peeche bhaagte bhaagte khud kichad mein gir gaya!"
        ),
    },
    {
        "title": "Funny Boy-এর রহস্যময় লাঞ্চবক্স",
        "story_bn": (
            "Funny Boy স্কুলে লাঞ্চবক্স খুলে অবাক হয়ে গেল। "
            "সে ভেবেছিল ভিতরে তার প্রিয় খাবার আছে। "
            "কিন্তু সেখানে ছিল শুধু একটা চামচ! "
            "পরে বুঝল আসল লাঞ্চবক্সটা সে বাড়িতেই রেখে এসেছে।"
        ),
        "story_hi": (
            "Funny Boy school mein lunch box kholkar hairaan ho gaya। "
            "Use laga andar uska favourite food hoga। "
            "Lekin andar sirf ek spoon tha! "
            "Baad mein pata chala asli lunch box ghar par hi reh gaya tha."
        ),
    },
    {
        "title": "Funny Boy-এর ঘুমন্ত অ্যালার্ম",
        "story_bn": (
            "সকালে Funny Boy-এর অ্যালার্ম বেজে উঠল। "
            "সে অ্যালার্ম বন্ধ করে আবার ঘুমিয়ে পড়ল। "
            "কিছুক্ষণ পরে উঠে দেখল সে দেরি করে ফেলেছে। "
            "তারপর সে বুঝল অ্যালার্মকে নয়, নিজের ঘুমকেই হারাতে হবে!"
        ),
        "story_hi": (
            "Subah Funny Boy ka alarm baja। "
            "Usne alarm band kiya aur phir so gaya। "
            "Thodi der baad utha to bahut late ho chuka tha। "
            "Tab use samajh aaya ki alarm ko nahi, apni neend ko harana padega!"
        ),
    },
    {
        "title": "Funny Boy-এর কথা বলা ব্যাগ",
        "story_bn": (
            "Funny Boy তার ব্যাগ থেকে অদ্ভুত শব্দ শুনতে পেল। "
            "সে ভয় পেয়ে ব্যাগ খুলল। "
            "ভিতর থেকে বের হলো তার খেলনা রোবট, যেটার ব্যাটারি চালু হয়ে গিয়েছিল। "
            "Funny Boy হাসতে হাসতে বলল, আজ ব্যাগও কথা বলতে শিখেছে!"
        ),
        "story_hi": (
            "Funny Boy ko apne bag se ajeeb awaaz sunai di। "
            "Usne darr kar bag khola। "
            "Andar uska toy robot tha jiska battery switch on ho gaya tha। "
            "Funny Boy hanskar bola, aaj mera bag bhi bolna seekh gaya!"
        ),
    },
]


def get_daily_story():
    today_number = date.today().toordinal()
    story = STORIES[today_number % len(STORIES)]

    return {
        "title": story["title"],
        "story_bn": story["story_bn"],
        "story_hi": story["story_hi"],
        "story_id": today_number % len(STORIES),
    }


if __name__ == "__main__":
    story = get_daily_story()

    print("=" * 60)
    print("FUNNY BOY DAILY STORY")
    print("=" * 60)
    print("Title:", story["title"])
    print()
    print("BENGALI:")
    print(story["story_bn"])
    print()
    print("HINDI:")
    print(story["story_hi"])
