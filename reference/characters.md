# Character library (assets/characters/)

Use these before asking the user for new images. Names are the pose keys for `hero()` / `cast()` / `hface()`.
Sources (for re-cutting or as AI references) are in each folder's `src/`.

## Hero — "The Mentor" (`assets/characters/mentor/`, `hero(c, "<pose>", ...)`)
| pose | look | good for |
|---|---|---|
| hips | hands on hips, aviators | confident default, hook |
| crossed | arms crossed, aviators | listening, judging, neutral stand |
| point_side | pointing right (hi-res) | pointing at a thing/cloud/book |
| point_you | pointing at the viewer | "you", CTA, follow |
| thumbs | thumbs up, grin | approval, "good idea", happy ending |
| coffee | holding black mug, smirk | relaxed, being served |
| walk | mid-stride walking right | entering with `hop` + `enter()` |
| search | crouched, magnifying glass | looking for something |
| phone | yelling into a phone | calling, complaining |
| flex | double biceps, shouting | chant, power, motivation |
| love | heart eyes, hands clasped, one leg up | infatuation, desire |
| shocked | hands on head, mouth open | bad news, reveal |
| facepalm | hand on face | embarrassment, foolishness |
| shrug | palms up | confusion, "what now?" |
| rain | soaked, briefcase, head down | dread, sad walk home |
| propose | one knee, open ring box | commitment, choosing |
| cry | crouched sobbing (REL 0.72) | despair |

Face cards (`hface(c, "<face>", x, y, size, t)`): cool, smirk, yell, shocked, love, cry, think, laugh, dizzy.

## Cast (`assets/characters/cast/`, `cast(c, "<pose>", ...)`)
| pose | who |
|---|---|
| good_wife / good_wife_tray | warm ponytail woman, yellow dress + apron (waving / serving coffee tray) |
| bad_wife / bad_wife_smug / bad_wife_money | huge curly red hair, purple dress (rolling pin yelling / arms crossed smirk / hugging $ bags, dollar eyes) |
| dream_girl | golden angel "ideal woman" (use via `gold_person()`) |
| shy / shy_shrug | timid girl, bangs over one eye, pink cardigan (hands clasped / helpless shrug) |
| bride | bride with veil and bouquet |
| mom | grandma-style mom, curlers, glasses, apron, arms open |
| smart | glasses, bun, navy dress, holding a book |
| chad | square-jaw rich guy, navy suit, crown, sunglasses, thumbs up |
| woman_a / woman_a_nag / woman_a_leave | black bob, green dress (smiling / shouting & pointing / walking off with red suitcase) |
| woman_b | afro, blue dress, hand on hip |
| woman_c | blonde ponytail, orange dress, curtsy |
| guy_1 / guy_2 | young skinny guys with heart eyes (orange tee / purple tee) |
| boy / girl | kids waving (REL 0.6) |
| old_mentor_sit / old_mentor_search / old_mentor_cry | the hero aged ~75 (sitting — draw `bench()` under him / cane + magnifier / crying with cane) |
| pregnant | pregnant woman in peach dress gently cradling belly |
| nursing_mom | mother in lavender dress cradling newborn in white blanket |
| warrior | prehistoric tribal warrior with fur vest and wooden spear |
| queen | elegant queen in burgundy gown with gold trim and gold crown |
| farm_boy | peasant boy in overalls holding pitchfork |
| village_girl | humble village girl in brown dress with apron, curtsy |
| handsome_broke | handsome guy in leather jacket pulling out empty pockets |
| genius | eccentric scientist in lab coat with clipboard |
