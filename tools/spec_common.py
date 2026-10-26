"""Helpers used to generate work/<slug>/reels.json (the reel spec) in code.
reel(...) builds one reel entry with the standard caption (English description
+ 'From <talk> by Sri Satyatmateertha Shripadangalavaru ...' + Kannada
description + English and Kannada hashtags). write(...) saves the spec.
The generators for the 2026-10-26 batch (ep01-ep04, sarkara) were throwaway
scripts that used this module; their output is the committed reels.json files,
which are the real source of truth. Pattern for a new source:
    from spec_common import *
    R=[reel(1,"topic-kebab",start,end,"Title lead","Title main",subs,desc_en,desc_kn,
            "#EnglishTag ...","#KannadaTag ...",ep_en,ep_kn)]
    write(slug, crop_x, source_title, source_url, note, R)
subs = [["English line", start_s, end_s], ...] in CLIP-RELATIVE seconds.
Optional per-reel extras: extra={"glitch_ok":[[a,b]],"hold_frames":[[a,b]]}.
Optional spec keys (add after write): "reframe":"fit" for non-16:9 sources.
"""
import json, os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
SPEAKER="Sri Satyatmateertha Shripadangalavaru"
BASE_EN="#Madhwa16 {tags} #SriUttaradiMath #Adhyatmavani #SatyatmateerthaShripadangalavaru #Pravachana #Dvaita #SanatanaDharma #HinduWisdom #Devotional #Shorts"
BASE_KN="#ಕನ್ನಡ #ಪ್ರವಚನ {tags} #ಮಧ್ವ"
def reel(num, topic, start, end, lead, main, subs, desc_en, desc_kn, tags_en, tags_kn, ep_en, ep_kn, extra=None):
    cap={"title": f"{lead} {main} 🙏 | Madhwa16".replace("  "," "),
         "description": f'{desc_en} 🙏 From "{ep_en}" by {SPEAKER} (Sri Uttaradi Math Adhyatmavani).',
         "description_kn": f'{desc_kn} ಶ್ರೀ ಸತ್ಯಾತ್ಮತೀರ್ಥ ಶ್ರೀಪಾದಂಗಳವರ “{ep_kn}” ಪ್ರವಚನದಿಂದ.',
         "hashtags": BASE_EN.format(tags=tags_en), "hashtags_kn": BASE_KN.format(tags=tags_kn)}
    r={"num":num,"topic":topic,"start":start,"end":end,"title_lead":lead,"title_main":main,"subs":subs,"caption":cap}
    if extra: r.update(extra)
    return r
def write(slug, crop_x, source_title, source_url, note, reels):
    d={"slug":slug,"crop_x":crop_x,"look":"v2","speaker":SPEAKER,"source_title":source_title,"source_url":source_url,"note":note,"reels":reels}
    os.makedirs(f"{ROOT}/work/{slug}",exist_ok=True)
    json.dump(d,open(f"{ROOT}/work/{slug}/reels.json","w"),ensure_ascii=False,indent=2)
    print("wrote",slug,len(reels),"reels")
