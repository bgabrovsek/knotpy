Splines would work wonderfully, especially the Hobby algorithm that I discovered
 later on, if only I could get a proper sequence of points in order
There are multiple ways to continue down the knot and I need to know how to 
 traverse it correctly, this information is baked into the PlanarDiagram 
 from what I've noticed, but I lack the understanding of PlanarDiagram 
 encoding to understand how to extract it
Without proper sequencing the splines or the Bezier plots do not work well
Also problems with sequencing through the knot arise when the node has 3 connections

I will be attempting a different approach to the simulation making it possible
 to utilise pre-existing plotting functions, namely --> draw_from_layout()

The main constriction is the requirement for tangential circles, which creates
 issues with any kind of disturbance of the tight CirclePacking algorithm
 as the proper connections get lost.
I have also attempted to adjust radiuses after the simulation for a sequence of
 just a few points, but the draw_from_layout() function demands entire dictionary
 of all points to be plotted

My next idea is making the simple sim but adding a few more points, namely
 for each connection two circles are touching, I would place a point at the 
 intersection of these two circles as additional points,
 run through the dispersion simulation making the points separate
Then we look at the points where the intersections of circles used to be,
 we calculate where the circles center should be by calculating the difference
 from ep0, ep1, ep2, ... to the circle center, and adjust position of center
 until distance to all points on edge is equal making that the new radius
Repeat this for each node and arc circle center and wed get a new radiuses and
 proper positions of circles that should still be touching the right circles
 (yes edge cases will be problematic, this is not finding a minimum in energy
 this is cutting off a simulation at just the right time so as not to lose.)
