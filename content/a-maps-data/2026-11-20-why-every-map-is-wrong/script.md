# Why every world map you know is wrong

Channel: `a-maps-data` · Format: long · Est. length: 6:05 (target 6:00 to 9:00)

## Script

**1.** In September 2026, 164 countries voted against the world map you grew up with. Here's what's wrong with it.
> On screen: 164 VOTES
> Visual: `count_up`
> Source: https://www.un.org/osaa/es/node/899

**2.** On that map, Greenland is about the size of Africa. In reality, Africa is fourteen times bigger. And Greenland isn't the only thing that's wrong.
> On screen: 14× BIGGER
> Visual: `comparison_split`
> Source: https://allafrica.com/stories/202508180103.html

**3.** Africa covers 30.37 million square kilometres. Russia, the largest country on Earth, covers 17.1 million. Africa is nearly twice the size of Russia, yet on most wall maps Russia looks far larger.
> On screen: AFRICA 30.37M · RUSSIA 17.1M
> Visual: `bar_compare`
> Source: https://allafrica.com/stories/202508180103.html

**4.** Greenland is even smaller than the Democratic Republic of the Congo. To understand why the map lies, we need to start with an orange.
> On screen: GREENLAND < DR CONGO
> Visual: `comparison_split`
> Source: https://www.worldatlas.com/articles/is-greenland-larger-than-africa.html

**5.** Try peeling an orange and pressing the peel flat on a table. It tears, or it stretches. There's no way to lay a curved surface flat without changing something. Every world map ever drawn has made that trade.
> On screen: YOU CAN'T FLATTEN A SPHERE
> Visual: `orange_peel`
> Source: https://www.johndcook.com/blog/2018/08/10/equal-earth-projection/

**6.** A map projection is simply a rule for that trade. It decides what to keep true: shapes, areas, distances or directions. You can keep some of them. You can never keep them all.
> On screen: SHAPE · AREA · DISTANCE · DIRECTION
> Visual: `grid_reveal`

**7.** In 1569, a Flemish mapmaker named Gerardus Mercator chose directions. His map was built for sailors.
> On screen: GERARDUS MERCATOR · 1569
> Visual: `timeline`
> Source: https://origin-exchange.autodesk.com/greenland-actual-size

**8.** On a Mercator map, a line of constant compass bearing is a straight line. A navigator could draw a straight line from port to port, read the angle, and hold that heading across the ocean.
> On screen: STRAIGHT LINE = CONSTANT BEARING
> Visual: `rhumb_line`
> Source: https://www.johndcook.com/blog/2018/08/10/equal-earth-projection/

**9.** For three centuries of ocean travel, that was worth almost any cost. The cost was area.
> Visual: `kinetic_text`

**10.** To keep angles true, Mercator stretches the map sideways the further you go from the equator, and then stretches it vertically by the same amount. Near the equator, almost nothing changes. Near the poles, everything balloons.
> On screen: STRETCH GROWS WITH LATITUDE
> Visual: `grid_stretch`
> Source: https://origin-exchange.autodesk.com/greenland-actual-size

**11.** The maths is simple. At a latitude of seventy-two degrees, roughly the middle of Greenland, areas are drawn about ten times too large. That's why Greenland looks like a continent.
> On screen: 72° N → ≈ 10× AREA
> Visual: `line_draw`
> Source: https://origin-exchange.autodesk.com/greenland-actual-size

**12.** It builds up quickly. At forty-five degrees north, around Milan or Montreal, areas are drawn twice as big as they should be. At sixty degrees, around Oslo or Anchorage, they're four times too big.
> On screen: 45° → 2× · 60° → 4×
> Visual: `line_draw`
> Source: https://origin-exchange.autodesk.com/greenland-actual-size

**13.** That's how Greenland, at 2.17 million square kilometres, ends up looking bigger than Australia, which is more than three times its size. Even Saudi Arabia is larger than Greenland.
> On screen: AUSTRALIA 7.6M > GREENLAND 2.17M
> Visual: `comparison_split`
> Source: https://origin-exchange.autodesk.com/greenland-actual-size

**14.** India is hit the other way. At 3.29 million square kilometres, India is about one and a half times the size of Greenland. But because India sits close to the equator, on a Mercator map it looks smaller.
> On screen: INDIA 3.29M > GREENLAND 2.17M
> Visual: `comparison_split`
> Source: https://allafrica.com/stories/202508180103.html

**15.** At the poles themselves, the stretch becomes infinite. A true Mercator map can never show the North or South Pole at all. It has to cut them off.
> On screen: THE POLES: ∞
> Visual: `grid_stretch`

**16.** Africa straddles the equator, so its size stays close to true. Europe and North America sit far to the north, so they look much bigger than they are.
> Visual: `map_highlight`
> Source: https://www.green.earth/blog/true-size-map-africa

**17.** Here's a way to feel it. Take the United States, China and India, and place them inside Africa. Together they cover about 22.75 million square kilometres. Africa still has more than seven million left over.
> On screen: 22.75M INSIDE 30.37M
> Visual: `shape_pack`
> Source: https://allafrica.com/stories/202508180103.html

**18.** So people have tried to fix the map. The best-known fix is the Gall-Peters projection. It keeps every area in proportion, so Africa finally looks as big as it is.
> On screen: GALL-PETERS
> Visual: `projection_morph`

**19.** But to do that, it stretches shapes. Africa and South America look long and thin, and many cartographers have criticised it for that.
> On screen: TRUE AREA · WARPED SHAPE
> Visual: `projection_morph`
> Source: https://www.esri.com/about/newsroom/arcuser/equal-earth/

**20.** In 2018, three cartographers, Bojan Šavrič, Bernhard Jenny and Tom Patterson, designed a newer option called Equal Earth. It keeps areas true, like Gall-Peters, but with gently curved sides that keep shapes looking natural.
> On screen: EQUAL EARTH · 2018
> Visual: `projection_morph`
> Source: https://pro.arcgis.com/en/pro-app/3.4/help/mapping/properties/equal-earth.htm

**21.** Its lines of latitude stay straight, so you can still compare how far north places are. And instead of stretching the poles out into a full-width line, it shrinks them to just over half the width of the equator.
> On screen: POLES ≈ 0.59 × EQUATOR
> Visual: `projection_morph`
> Source: https://pro.arcgis.com/en/pro-app/3.4/help/mapping/properties/equal-earth.htm

**22.** It was quickly adopted by NASA's Goddard Institute for Space Studies.
> On screen: ADOPTED BY NASA GISS
> Visual: `kinetic_text`
> Source: https://pro.arcgis.com/en/pro-app/3.4/help/mapping/properties/equal-earth.htm

**23.** Equal Earth exists because of a classroom argument. In March 2017, Boston Public Schools switched to the Gall-Peters map. Its warped shapes caused a row among mapmakers, and that row is what pushed Šavrič, Jenny and Patterson to design something better.
> On screen: BOSTON, 2017
> Visual: `timeline`
> Source: https://en.wikipedia.org/wiki/Equal_Earth_projection

**24.** Then the argument went global. African advocacy groups launched a campaign called Correct the Map, asking institutions to drop Mercator for Equal Earth. The African Union backed it.
> On screen: #CORRECTTHEMAP
> Visual: `kinetic_text`
> Source: https://en.wikipedia.org/wiki/Equal_Earth_projection

**25.** On the fourth of September 2026, the UN General Assembly passed a resolution with that name. 164 countries voted for it, one voted against, and six abstained.
> On screen: 164 · 1 · 6
> Visual: `bar_compare`
> Source: https://www.un.org/osaa/es/node/899

**26.** It doesn't ban Mercator, and it doesn't force anyone to change. It encourages governments, schools and tech companies to use equal-area maps when size matters.
> On screen: NO BAN · ENCOURAGES EQUAL-AREA
> Visual: `grid_reveal`
> Source: https://www.un.org/osaa/es/node/899

**27.** Supporters say the old map shrinks Africa in people's minds. The one country that voted no, the United States, called the resolution an ideological agenda and a distraction from real problems.
> On screen: FOR · AGAINST
> Visual: `comparison_split`
> Source: https://www.khaleejtimes.com/world/africa-bigger-us-smaller-un-adopts-new-map-continents

**28.** So which map is right? None of them. And all of them. Each one is an answer to a question.
> On screen: WHICH MAP IS RIGHT?
> Visual: `grid_reveal`

**29.** Even the UN resolution says so. It accepts that Mercator is still useful for navigation at sea and in the air. The fight was never about the sailor's map. It was about the map on the classroom wall.
> On screen: STILL USEFUL AT SEA
> Visual: `rhumb_line`
> Source: https://ground.news/article/9be8f433-1148-46c9-b34d-f9f7344d8f49

**30.** If you're steering a ship by compass, Mercator is still a brilliant tool. If you're comparing how big countries are, you want an equal-area map. If you want both, you want a globe.
> On screen: NAVIGATE · COMPARE · BOTH
> Visual: `grid_reveal`

**31.** The problem was never Mercator. The problem was using a sailor's tool to teach the size of the world.
> Visual: `kinetic_text`

**32.** Next time you see a world map, ask two questions. What is this map keeping true? And what did it give up to do that?
> On screen: WHAT DID IT GIVE UP?
> Visual: `comparison_split`

## Post copy

Title: Why every world map you know is wrong

Description: Mercator, Gall-Peters, Equal Earth: why no flat map can be true, and how to pick the right one.

Tags: maps, Mercator, map projections, geography, Equal Earth
