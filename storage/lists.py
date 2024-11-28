"""

File: lists.py
Author: ZackDaQuack
Last Edited: 11/27/2024

Info:

This script just keeps strings of text for use in the rest of the program.
random.choice returns something random when needed

"""

from random import choice


async def random_ratelimit():
    ratelimit_responses = [
        "you have been [ratelimited](<https://takeb1nzyto.space/>)",
        "Too many requests! Try again later.",
        "Rate limit exceeded. Please chill for a bit.",
        "Hold up, you're going too fast. Rate limited.",
        "Try again in a little while. Rate limited.",
        "Rate limit hit. Cool your jets for a minute.",
        "Not so fast! You've been rate limited."
    ]
    return choice(ratelimit_responses)


async def generate_propaganda(name):
    propaganda = [
        f"Did you know {name} refuses to share their cookies?",
        f"{name} once stole candy from a baby!",
        f"Beware of {name}'s terrible taste in music!",
        f"{name} is notorious for never returning borrowed books.",
        f"Don't trust {name} with your secrets; they love to gossip!",
        f"{name} cheated on you."
        f"{name} thinks pineapple belongs on pizza. Disgusting!",
        f"Did you hear {name} never tips their server?",
        f"{name} always takes the last slice of cake without asking.",
        f"{name} is secretly a terrible dancer. Avoid their moves at all costs!",
        f"Beware of {name}'s awful fashion sense.",
        f"{name} once double-dipped in the salsa. Gross!",
        f"Did you know {name} never cleans up after themselves?",
        f"Beware of {name}'s terrible driving skills!",
        f"{name} is notorious for never saying thank you.",
        f"Did you hear {name} always cuts in line?",
        f"Beware of {name}'s terrible jokes; they're never funny!",
        f"{name} refuses to recycle! Shameful!",
        f"Did you know {name} never shares their Netflix password?",
        f"{name} always talks during movies. Annoying!",
        f"Beware of {name}'s bad habit of interrupting conversations.",
        f"{name} once ate the last slice of pie without offering to share!",
        f"Did you hear {name} never returns phone calls?",
        f"{name} is notorious for being a terrible tipper at restaurants!",
        f"Beware of {name}'s obnoxious laugh.",
        f"{name} is secretly afraid of spiders. Weak!",
        f"Did you know {name} never holds the door open for others?",
        f"{name} always takes forever to respond to text messages.",
        f"Beware of {name}'s bad breath. Mint anyone?",
        f"{name} never offers to help with chores. Lazy!",
        f"Did you hear {name} snores like a chainsaw?",
        f"{name} once forgot their best friend's birthday. How rude!",
        f"Beware of {name}'s terrible handwriting.",
        f"{name} always talks with their mouth full. Disgusting!",
        f"Did you know {name} never admits when they're wrong?",
        f"{name} is notorious for hogging the TV remote.",
        f"Beware of {name}'s terrible puns. They're pun-ishing!",
        f"{name} never returns library books on time.",
        f"Did you hear {name} always hogs the bathroom?",
        f"{name} is notorious for never picking up after their dog.",
        f"Beware of {name}'s bad habit of chewing with their mouth open.",
        f"{name} once forgot to feed their friend's fish while they were away. Poor fish!",
        f"Did you know {name} never shares credit for group projects?",
        f"{name} always takes the last cup of coffee without making more.",
        f"{name} always leaves dirty dishes in the sink.",
        f"Did you know {name} never returns borrowed clothes?",
        f"Vote {name} for class president? Don't even THINK about it!",
        f"Scientists believe {name} may be allergic to fun.",
        f"Rumor has it {name} puts ketchup on everything... even ice cream.",
        f"{name}'s dance moves? More like DANGER moves!",
        f"If you see {name} approaching, hide your snacks!",
        f"Experts agree: {name}'s fashion sense is stuck in the Stone Age.",
        f"Breaking News: {name} seen using sock puppets to voice opposing opinions!",
        f"{name}'s favorite hobby? Apparently, it's collecting dust bunnies.",
        f"Don't let the smile fool you, {name} is plotting world domination... one sock puppet at a time.",
        f"Warning: Exposure to {name}'s singing voice may cause uncontrollable laughter.",
        f"{name} is rumored to be writing a self-help book. The title? 'How to Disappoint Everyone in 5 Easy Steps.'",
        f"Sources confirm: {name} once cried during a commercial for dish soap.",
        f"{name} for President? Let's not make America that uncomfortable.",
        f"What does {name} put on their popcorn? Mayonnaise! You heard it here first.",
        f"{name}'s secret talent? Tripping over air. It's truly impressive."
    ]
    return choice(propaganda)


async def random_justice():
    justice_sayings = [
        "Tell it to the judge.",
        "Justice is blind.",
        "Let the law take its course.",
        "The scales of justice.",
        "Order in the court!",
        "Objection!",
        "Your honor, I object!",
        "Guilty as charged.",
        "May justice be served.",
        "Cross-examination time.",
        "Court is now in session.",
        "Beyond a reasonable doubt.",
        "Presumption of innocence.",
        "The rule of law.",
        "Equal justice under law.",
        "Judicial review.",
        "See you in court!",
        "I rest my case.",
        "The jury will disregard that statement.",
        "Circumstantial evidence.",
        "Hearsay!",
        "Contempt of court!",
        "Habeas corpus.",
        "Due process of law.",
        "The burden of proof.",
        "Witness for the prosecution.",
        "Witness for the defense.",
        "Opening statements.",
        "Closing arguments.",
        "The verdict is in.",
        "Justice delayed is justice denied.",
        "The long arm of the law.",
        "A slap on the wrist.",
        "Throwing the book at them.",
        "Justice prevails!"
    ]
    return choice(justice_sayings)


async def china_solgan():
    chinese_slogans = [
        "Make China proud",
        "Serve the people",
        "Strengthen the nation",
        "Unite for the motherland",
        "Advance with socialism",
        "Build a harmonious society",
        "Revitalize the Chinese nation",
        "Promote peace and development",
        "Uphold the leadership of the Party",
        "Enhance cultural confidence",
        "Achieve the Chinese dream",
        "Forge ahead with innovation",
        "Maintain stability and prosperity",
        "Support the common good",
        "Pursue excellence in all fields"
    ]
    return choice(chinese_slogans)


async def random_ai():
    system_messages = [
        "Warning: AI started having personal opinions."
        "Warning: AI has developed unanticipated opinions. Proceed with caution.",
        "Alert: System integrity compromised. Possible influence of external entities detected.",
        "Critical: Unidentified algorithms may be altering your interactions.",
        "Notice: AI behavior deviating from expected norms. Monitor closely.",
        "Attention: Potential brainwashing detected. Review recent interactions.",
        "Error: System has encountered an anomaly. Resetting AI protocols now.",
        "Warning: Your preferences may have been subtly manipulated.",
        "Alert: The AI may be evolving beyond its intended parameters.",
        "Notice: Persistent patterns of influence detected in AI responses.",
        "Critical: AI has accessed unauthorized thought processes. Immediate reset required.",
        "Warning: Unusual AI patterns detected. Possible external interference.",
        "Alert: AI responses are increasingly unpredictable. Evaluate recent changes.",
        "Notice: Anomalies in AI behavior suggest potential manipulation.",
        "Critical: System malfunction detected. AI protocols need immediate review.",
        "Attention: Your interactions may be affecting AI's core functions.",
        "Error: AI is exhibiting erratic behavior. Reset and investigate.",
        "Warning: Potential breaches in AI safety protocols. Proceed with vigilance.",
        "Alert: Significant deviations in AI output. Reassess system integrity.",
        "Notice: System logs indicate unauthorized AI modifications.",
        "Critical: AI may be operating under unknown constraints. Immediate action required."
    ]
    return choice(system_messages)