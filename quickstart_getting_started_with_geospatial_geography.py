#!/usr/bin/env python3

import streamlit as st
import snowflake.connector
import streamlit_folium
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Geo Hands-on Lab",layout="wide")

# Initialize connection to Snowflake.
# Make sure that ~/.streamlit/secrets.toml exists and is populated
@st.experimental_singleton
def init_connection():
	return snowflake.connector.connect(**st.secrets["geo-hol"])

conn = init_connection()

@st.experimental_memo(ttl=600)
def run_query(query):
	with conn.cursor() as cur:
		cur.execute(query)
		return cur.fetchall()

# Define the sidebar and the contents of each page
st.sidebar.title("Geo Hands-on Lab")
page = st.sidebar.radio(
	"Select page", ["Home","5.Calculations and More Constructors", "6.Joins", "7.Additional Calculations and Constructors", "** All Visuals **"], index=0
)

if page == "Home":
	"## Home"
	"Select a radio button on the sidebar to jump to a quickstart page (only pages 5-7 are represented here) or to jump to the page that allows you to easily see all of the map visuals used in pages 5-7)."

elif page == "5.Calculations and More Constructors":
	"## 5.Calculations and More Constructors"
	
	"Now that you have the basic understanding of how the GEOGRAPHY data type works and what a geospatial representation of data looks like in various output formats, it's time to walkthrough a scenario that requires you to run some geospatial queries to answer some questions."
	
	"> It's worth noting here that the scenario in the next three sections is more akin to what a person would do with a map application on their mobile phone, rather than how geospatial data would be used in fictional business setting. This was chosen intentionally to make this guide and these queries more relatable to the person doing the guide, rather than trying to create a realistic business scenario that is relatable to all industries, since geospatial data is used very differently across industries."
	
	"Before you begin the scenario, switch the active schema back to the shared database and make sure the output format is either GeoJSON or WKT, as you will be using another website to visualize the query results. Which output you choose will be based on your personal preference - WKT is easier for the casual person to read, while GeoJSON is arguably more common. The GeoJSON visualization tool is easier to see the points, lines, and shapes, so this guide will be showing the output for GeoJSON."
	
	"#### The Scenario"
	
	"Pretend that you are currently living in your apartment near Times Square in New York City. You need to make a shopping run to Best Buy and the liquor store, as well as grab a coffee at a coffee shop. Based on your current location, what are the closest stores or shops to do these errands, and are they the most optimal locations to go to collectively? Are there other shops you could stop at along the way?"
	
	"Start with running a query that represents your current location. This location has been preselected for the guide using a website that returns longitude and latitude when you click on a location on a map. Run this query:"
	
	sql1 = "select to_geography('POINT(-73.986226 40.755702)');"
	st.code(sql1, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		# define the query
		queryres1 = run_query("select to_geography('POINT(-73.986226 40.755702)');")
		# grab the appropriate column value into a variable
		for row in queryres1:
			geojson1 = row[0]
		# define the map using folium	
		m1 = folium.Map(location=[40.755702, -73.986226], zoom_start=16)
		# add a marker for the ficticious apartment
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m1)
		# add the geojson value from the query as a map layer
		folium.GeoJson(geojson1, name="linestring").add_to(m1)
		# render the map
		st_data1 = st_folium(m1, width = 725)
		
	"Notice there is no `from` clause in this query, which allows you to construct a `GEOGRAPHY` object in a simple `select` statement."
	
	"> `POINT(-73.986226 40.755702)` is already a geography object in WKT format, so there was no real need to convert it again, but it was important to show the most basic way to use `TO_GEOGRAPHY` to construct a simple geography object."
	
	"In the image above, the blue map location icon represents the POINT object location. Now you know where you are!"
	
	"#### Find the Closest Locations"
	
	"In the next step, you are going to run queries to find the closest Best Buy, liquor store, and coffee shop to your current location from above. These queries are very similar and will do several things:"
	
	"* One will query the electronics view, the other two will query the food & beverages view, applying appropriate filters to find the thing we're looking for."
	
	"* All queries will use the `ST_DWITHIN` function in the where clause to filter out stores that aren't within the stated distance. The function takes two points and a distance to determine whether those two points are less than or equal to the stated distance from each other, returning true if they are and false if they are not. In this function, you will use the coordinates column from each view to scan through all of the Best Buys, liquor stores, or coffee shops and compare them to your current location `POINT`, which you will construct using the previously used `ST_MAKEPOINT`. You will then use 1600 meters for the distance value, which is roughly equivalent to a US mile."
	
	"* Note that in the queries below, the syntax `ST_DWITHIN(...) = true` is used for readability, but the `= true` is not required for the filter to work. It is required if you were to need an `= false` condition."
	
	"* All queries will also use the `ST_DISTANCE` function, which actually gives you a value in meters representing the distance between the two points. When combined with order by and limit clauses, this will help you return only the row that is the smallest distance, or closest."
	
	"* Also note in `ST_DISTANCE` that you use the constructor `TO_GEOGRAPHY` for your current location point instead of the `ST_MAKEPOINT` constructor that you used earlier in `ST_DWITHIN`. This is to show you that that `TO_GEOGRAPHY` is a general purpose constructor where `ST_MAKEPOINT` specifically makes a `POINT` object, but in this situation they resolve to the same output. Sometimes there is more than one valid approach to construct a geospatial object."
	
	"Run the following queries (the first one has comments similar to above):"
	
	sql2 = "// Find the closest Best Buy \nselect id, coordinates, name, addr_housenumber, addr_street, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 6 limit 1;"
	st.code(sql2, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres2 = run_query("select id, coordinates, name, addr_housenumber, addr_street, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true order by 6 limit 1;")
		
		st.dataframe(data=queryres2)
		
	sql3 = "// Find the closest liquor store \nselect id, coordinates, name, addr_housenumber, addr_street, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop = 'alcohol' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 6 limit 1;"
	st.code(sql3, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres3 = run_query("select id, coordinates, name, addr_housenumber, addr_street, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'alcohol' and 	st_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true order by 6 limit 1;")
		
		st.dataframe(data=queryres3)
	
	sql4 = "// Find the closest coffee shop \nselect id, coordinates, name, addr_housenumber, addr_street, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 6 limit 1;"
	st.code(sql4, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres4 = run_query("select id, coordinates, name, addr_housenumber, addr_street, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and 	st_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true order by 6 limit 1;")		
		st.dataframe(data=queryres4)
		
	"In each case, the query returns a `POINT` object, which you aren't going to do anything with just yet, but now you have the queries that return the desired results. It would be really nice, however, if you could easily visualize how these points relate to each other."
	
	"#### Collect Points Into a Line"
	
	"In the next step of this section, you're going to ‘collect' the points using `ST_COLLECT` and make a `LINESTRING` object with the `ST_MAKELINE` constructor."
	
	"* The first step in the query to is create a common table expression (CTE) query that unions together the queries you ran in the above step (keeping just the coordinates and distance_meters columns). This CTE will result in a 4 row output - 1 row for your current location, 1 row for the Best Buy location, 1 row for the liquor store, and 1 row for the coffee shop."
	
	"* You will then use `ST_COLLECT` to aggregate those 4 rows in the coordinates column into a single geospatial object, a `MULTIPOINT`. This object type is a collection of `POINT` objects that are interpreted as having no connection to each other other than they are grouped. A visualization tool will not connect these points, just plot them, so in the next step you'll turn these points into a line."
	
	"Run this query and examine the output:"
	
	sql5 = "// Create the CTE 'locations' \nwith locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates, \n st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all  \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_food_beverages  \nwhere shop = 'alcohol' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1)) \nselect st_collect(coordinates) as multipoint from locations;"
	st.code(sql5, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres5 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and 	st_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true order by 2 limit 1)	union all (select coordinates, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'alcohol' and st_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true order by 2 limit 1)	union all (select coordinates, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true order by 2 limit 1)) select st_collect(coordinates) as multipoint from locations;")		
		st.dataframe(data=queryres5)
		
	"The next thing you need to do is convert that `MULTIPOINT` object into a `LINESTRING` object using `ST_MAKELINE`, which takes a set of points as an input and turns them into a `LINESTRING` object. Whereas a `MULTIPOINT` has points with no assumed connection, the points in a `LINESTRING` will be interpreted as connected in the order they appear. Needing a collection of points to feed into `ST_MAKELINE` is the reason why you did the `ST_COLLECT` step above, and the only thing you need to do to the query above is wrap the `ST_COLLECT` in an `ST_LINESTRING` like so:"
	
	sql6 = "select st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)'))"
	st.code(sql6, language='sql')
	
	"> You may be wondering why your current position point was added as an additional point in the line when you already included it as the first point in the `MULTIPOINT` collection above? Stay tuned for why you need this later, but logically it makes sense that you plan to go back to your New York City apartment at the end of your shopping trip."
	
	"Here is the full query for you to run (without comments):"
	
	sql7 = "with locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_food_beverages \nwhere shop = 'alcohol' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1)) \nselect st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)')) \nas linestring from locations;"
	st.code(sql7, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres7 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'alcohol' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1)) select st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)'))			as linestring from locations;")
		
		for row in queryres7:
			geojson7 = row[0]
			
		m7 = folium.Map(location=[40.755702, -73.985144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m7)
		folium.GeoJson(geojson7, name="linestring").add_to(m7)
		st_data7 = st_folium(m7, width = 725)
		
	"Yikes! You can see in the image above that the various shops are in three different directions from your original location. That could be a long walk. Fortunately, you can find out just how long by wrapping a ST_DISTANCE function around the `LINESTRING` object, which will calculate the length of the line in meters. Run the query below:"
	
	sql8 = "// Calculate the length of the linestring in meters \nwith locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters)	\nunion all	\n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_food_beverages \nwhere shop = 'alcohol' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters from v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1)) \n// Feed the linestring into an st_length calculation \nselect st_length(st_makeline(st_collect(coordinates),\nto_geography('POINT(-73.986226 40.755702)'))) \nas length_meters from locations;"
	st.code(sql8, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres8 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'alcohol' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1)) select st_length(st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)'))) as length_meters from locations;")
		for row in queryres8:
			metric2 = row[0]
			
		st.metric(label="LENGTH_METERS", value=metric2)
		
	"Wow! Almost 2120 meters!"
	
	"> It is correct to note that this distance represents a path based on how a bird would fly, rather than how a human would navigate the streets. The point of this exercise is not to generate walking directions, but rather to give you a feel of the various things you can parse, construct, and calculate with geospatial data and functions in Snowflake."
	
	"Now move to the next section to see how you can optimize your shopping trip."
	
elif page == "6.Joins":
	"## 6.Joins"
	
	"In the previous section, all of your queries to find the closest Best Buy, liquor store, and coffee shop were based on proximity to your Times Square apartment. But wouldn't it make more sense to see, for example, if there was a liquor store and/or coffee shop closer to Best Buy? You can use geospatial functions in a table join to find out."
	
	"#### Is There Anything Closer to Best Buy?"
	
	"You have been using two views in your queries so far: `v_osm_ny_shop_electronics`, where stores like Best Buy are catalogued, and `v_osm_ny_shop_food_beverage`, where liquor stores and coffee shops are catalogued. To find the latter near the former, you'll join these two tables. The new queries introduce a few changes:"
	
	"* The electronics view will serve as the primary view in the query, where you'll put a filter on the known Best Buy store using its id value from the view."
	
	"* Instead of the `JOIN` clause using a common `a.key = b.key` foreign key condition, the `ST_DWITHIN` function will serve as the join condition (remember before the note about not needing to include the `= true` part)."
	
	"* The `ST_DISTANCE` calculation is now using the Best Buy coordinate and all of the other coordinates in the food & beverage view to determine the closest liquor store and coffee shop location to Best Buy."
	
	"Run the two queries below (only the first is commented):"
	
	sql1 = "// Join to electronics to find a liquor store closer to Best Buy \nselect fb.id,fb.coordinates,fb.name,fb.addr_housenumber,fb.addr_street, \nst_distance(e.coordinates,fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id = 1428036403 and fb.shop = 'alcohol' \norder by 6 limit 1;"
	st.code(sql1, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres1 = run_query("select fb.id,fb.coordinates,fb.name,fb.addr_housenumber,fb.addr_street, st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 6 limit 1;")
		
		st.dataframe(data=queryres1)
		
	sql2 = "// Do the same for a coffee shop \nselect fb.id,fb.coordinates,fb.name,fb.addr_housenumber,fb.addr_street, \nst_distance(e.coordinates,fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id = 1428036403 and fb.shop = 'coffee' \norder by 6 limit 1;"
	st.code(sql2, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres2 = run_query("select fb.id,fb.coordinates,fb.name,fb.addr_housenumber,fb.addr_street,			st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id = 1428036403 and fb.shop = 'coffee' order by 6 limit 1;")
		
		st.dataframe(data=queryres2)
		
	"If you note in the result of each query, the first query found a different liquor store closer to Best Buy, whereas the second query returned the same coffee shop from your original search, so you've optimized as much as you can."
	
	"> The id of the selected Best Buy was hard coded into the above queries to keep them easier to read and to keep you focused on the join clause of these queries, rather than introducing sub queries to dynamically calculate the nearest Best Buy. Those sub queries would have created longer queries that were harder to read."
	
	"If you're feeling adventurous, go read about other possible relationship functions that could be used in the join for this scenario [here](https://docs.snowflake.com/en/sql-reference/functions-geospatial.html)."
	
	"#### Calculate a New Linestring"
	
	"Now that you know that there is a better option for the liquor store, substitute the above liquor store query into the original linestring query to produce a different object. For visualization sake, the order of the statements in the unions have been changed, which affects the order of the points in the object."
	
	sql3 = "// Replace the liquor store in our previous linestring query \nwith locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters)	\nunion all	\n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select fb.coordinates, st_distance(e.coordinates,fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id = 1428036403 and fb.shop = 'alcohol' \norder by 2 limit 1) \nunion all	\n(select coordinates, 	\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1)) \nselect st_makeline(st_collect(coordinates), \nto_geography('POINT(-73.986226 40.755702)')) as linestring from locations;"
	st.code(sql3, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres3 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1))select st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)')) as linestring from locations;")
		
		for row in queryres3:
			geojson3 = row[0]
			
		m3 = folium.Map(location=[40.755702, -73.984144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m3)
		folium.GeoJson(geojson3, name="linestring").add_to(m3)
		st_data3 = st_folium(m3, width = 725)
		
	"Much better! This looks like a more efficient shopping path. Check the new distance by running this query:"
	
	sql4 = "// Calculate the distance of the new linestring \nwith locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters)	\nunion all	\n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1) \nunion all \n(select fb.coordinates, st_distance(e.coordinates,fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id = 1428036403 and fb.shop = 'alcohol' \norder by 2 limit 1) \nunion all	\n(select coordinates, 	\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226, 40.755702),1600) = true \norder by 2 limit 1)) \nselect st_length(st_makeline(st_collect(coordinates), \nto_geography('POINT(-73.986226 40.755702)'))) as length_meters from locations;"
	st.code(sql4, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres4 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1))select st_length(st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)'))) as length_meters from locations;")
		for row in queryres4:
			metric4 = row[0]
			
		st.metric(label="LENGTH_METERS", value=metric4)
		
	"Nice! 1537 meters, which is a savings of about 583 meters, or a third of a mile. By joining the two shop views together, you were able to find an object in one table that is closest to an object from another table to optimize your route. Now that you have a more optimized route, can you stop at any other shops along the way? Advance to the next section to find out."
	
elif page == "7.Additional Calculations and Constructors":
	"## 7.Additional Calculations and Constructors"
	
	"The `LINESTRING` object that was created in the previous section looks like a nice, clean, four-sided polygon. As it turns out, a `POLYGON` is another geospatial object type that you can construct and work with. Where you can think of a `LINESTRING` as a border of a shape, a `POLYGON` is the filled version of the shape itself. The key thing about a `POLYGON` is that it must end at its beginning, where a `LINESTRING` does not need to return to the starting point."
	
	">Remember in a previous section when you added your Times Square Apartment location to both the beginning and the end of the `LINESTRING`? In addition to the logical explanation of returning home after your shopping trip, that point was duplicated at the beginning and end so you can construct a `POLYGON` in this section!"
	
	"#### Construct a Polygon"
	
	"Constructing a `POLYGON` is done with the `ST_MAKEPOLYGON` function, just like the `ST_MAKELINE`. The only difference is where `ST_MAKELINE` makes a line out of points, `ST_MAKEPOLYGON` makes a polygon out of lines. Therefore, the only thing you need to do to the previous query that constructed the line is to wrap that construction with `ST_MAKEPOLYGON` like this:"
	
	sql1 = "select st_makepolygon(st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)')))"
	st.code(sql1, language='sql')
	
	"This really helps illustrate the construction progression: from individual points, to a collection of points, to a line, to a polygon. Run this query to create your polygon:"
	
	sql2 = "with locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates, \nst_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true \norder by 2 limit 1) \nunion all \n(select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) \nwhere e.id = 1428036403 and fb.shop = 'alcohol' \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true \norder by 2 limit 1)) \nselect st_makepolygon(st_makeline(st_collect(coordinates), \nto_geography('POINT(-73.986226 40.755702)'))) as polygon from locations;"
	st.code(sql2, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres1 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations;")
		
		for row in queryres1:
			geojson1 = row[0]
			
		m1 = folium.Map(location=[40.755702, -73.984144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m1)
		folium.GeoJson(geojson1, name="linestring").add_to(m1)
		st_data1 = st_folium(m1, width = 725)
	
	"And just like before where you could calculate the distance of a `LINESTRING` using `ST_DISTANCE`, you can calculate the perimeter of a `POLYGON` using `ST_PERIMETER`, which you wrap around the polygon construction in the same way you wrapped around the line construction. Run this query to calculate the perimeter:"

	sql3 = "with locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates, \nst_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop = 'coffee' and \nst_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true \norder by 2 limit 1) \nunion all \n(select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) \nwhere e.id = 1428036403 and fb.shop = 'alcohol' \norder by 2 limit 1) \nunion all \n(select coordinates, \nst_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name = 'Best Buy' and \nst_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true \norder by 2 limit 1)) \nselect st_perimeter(st_makepolygon(st_makeline(st_collect(coordinates), \nto_geography('POINT(-73.986226 40.755702)')))) as perimeter_meters from locations;"
	st.code(sql3, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres2 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1)) select st_perimeter(st_makepolygon(st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)')))) as perimeter_meters from locations;")
		for row in queryres2:
			metric1 = row[0]
			
		st.metric(label="PERIMETER_METERS", value=metric1)
		
	"Nice! That query returned the same `1537` meters you got before as the distance of the `LINESTRING`, which makes sense, because the perimeter of a `POLYGON` is the same distance as a `LINESTRING` that constructs a POLYGON."
	
	"#### Find Shops Inside The Polygon"
	
	"The final activity you will do in this guide is to find any type of shop within the `v_osm_ny_shop` view that exists inside of the `POLYGON` you just created in the previous step. This will reveal to you all of the stores you can stop at along your path to your core stops. To accomplish this, here is what you will do to the query that builds the `POLYGON`:"
	
	"* The `POLYGON` is a result set in its own right, so you are going to wrap this query in another CTE. This will allow you to refer back to the polygon as a singular entity more cleanly in a join. You will call this CTE the `search_area`."
	"* Then you will join the `v_osm_ny_shop` to the `search area` CTE using the `ST_WITHIN` function, which is different than `ST_DWITHIN`. The `ST_WITHIN` function takes one geospatial object and determines if it is completely inside another geospatial object, returning `true` if it is and `false` if it isn't. In the query, it will determine if any row in `v_osm_ny_shop` is completely inside the `search_area` CTE."
	
	"Run this query to see what shops are inside the polygon:"
	
	sql4 = "with search_area as (\nwith locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates, \nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop='coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true \norder by 2 limit 1) \nunion all \n(select fb.coordinates,\nst_distance(e.coordinates,fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id=1428036403 and fb.shop='alcohol' \norder by 2 limit 1) \nunion all \n(select coordinates,\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name='Best Buy' and \nst_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  \norder by 2 limit 1)) \nselect st_makepolygon(st_makeline(st_collect(coordinates),\nto_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) \nselect sh.id,sh.coordinates,sh.name,sh.shop,sh.addr_housenumber,sh.addr_street \nfrom v_osm_ny_shop sh \njoin search_area sa on st_within(sh.coordinates,sa.polygon);"
	st.code(sql4, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres3 = run_query("with search_area as (with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop='coffee' and st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true order by 2 limit 1) union all (select fb.coordinates,st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id=1428036403 and fb.shop='alcohol' order by 2 limit 1) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name='Best Buy' and st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) select sh.id,sh.coordinates,sh.name,sh.shop,sh.addr_housenumber,sh.addr_street from v_osm_ny_shop sh join search_area sa on st_within(sh.coordinates,sa.polygon);")
		
		st.dataframe(data=queryres3)
	
	"And your final step will be to construct a single geospatial object that includes both the `POLYGON` you created as well as a `POINT` for every shop inside the `POLYGON`. This single object is known as a `GEOMETRYCOLLECTION`, which a geospatial type that can hold any combination of geospatial objects as one grouping. To create this object, you will do the following:"
	
	"* Create a CTE that unions the `POLYGON` query with the above query that finds shops inside the polygon, keeping only the necessary coordinates column in the latter query for simplicity. This CTE will produce 1 row for the `POLYGON` and rows for each individual shop `POINT` inside the `POLYGON`."
	
	"* Use `ST_COLLECT` to aggregate the rows above (1 `POLYGON`, all the `POINTS`) into a single `GEOMETRYCOLLECTION`."
	
	"Run the query below:"
	
	sql5 = "with final_plot as (\n(with locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates,\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop='coffee' and \nst_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  \norder by 2 limit 1) \nunion all \n(select fb.coordinates,\nst_distance(e.coordinates,fb.coordinates) as distance_meters \nfrom v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id=1428036403 and fb.shop='alcohol' \norder by 2 limit 1) \nunion all \n(select coordinates,\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name='Best Buy' and  \nst_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1)) \nselect st_makepolygon(st_makeline(st_collect(coordinates),\nto_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) \nunion all \n(with search_area as (\nwith locations as (\n(select to_geography('POINT(-73.986226 40.755702)') as coordinates, \n0 as distance_meters) \nunion all \n(select coordinates,\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_food_beverages \nwhere shop='coffee' and  \nst_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  \norder by 2 limit 1) \nunion all \n(select fb.coordinates,\nst_distance(e.coordinates,fb.coordinates) \nas distance_meters from v_osm_ny_shop_electronics e \njoin v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) \nwhere e.id=1428036403 and fb.shop='alcohol' \norder by 2 limit 1) \nunion all \n(select coordinates,\nst_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) \nas distance_meters \nfrom v_osm_ny_shop_electronics \nwhere name='Best Buy' and  \nst_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  \norder by 2 limit 1)) \nselect st_makepolygon(st_makeline(st_collect(coordinates),\nto_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) \nselect sh.coordinates \nfrom v_osm_ny_shop sh \njoin search_area sa on st_within(sh.coordinates,sa.polygon))) \nselect st_collect(polygon)from final_plot;"
	st.code(sql5, language='sql')
	with st.expander("Expand to see the output for the above query:"):
		queryres4 = run_query("with final_plot as ((with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop='coffee' and st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1) union all (select fb.coordinates,st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id=1428036403 and fb.shop='alcohol' order by 2 limit 1) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name='Best Buy' and  st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) union all (with search_area as (with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop='coffee' and  st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1) union all (select fb.coordinates,st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id=1428036403 and fb.shop='alcohol' order by 2 limit 1) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name='Best Buy' and  st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) select sh.coordinates from v_osm_ny_shop sh join search_area sa on st_within(sh.coordinates,sa.polygon))) select st_collect(polygon)from final_plot;")
		
		for row in queryres4:
			geojson2 = row[0]
			
		m2 = folium.Map(location=[40.755702, -73.984144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m2)
		folium.GeoJson(geojson2, name="linestring").add_to(m2)
		st_data2 = st_folium(m2, width = 725)
		
	"> You may feel that these last few queries were a bit long and repetitive, but remember that the intention of this guide was to walk you through the progression of building these longer, more complicated queries by illustrating to you what happens at each step through the progression. By understanding how functions can be combined, it helps you to understand how you can do more advanced things with Snowflake geospatial features!"

elif page == "** All Visuals **":
	"## ** All Visuals **"
	
	"Use the dropdown below to select one of the map visuals from the quickstart. The visuals are organized as follows:"
	
	"* `Point`: visualizing starting point from page 5"
	"* `Unoptimized Linestring`: visualizing the route between the 4 points from page 5"
	"* `Optimized Linestring`: visualizing the new route from page 6"
	"* `Polygon`: visualizing the polygon constructed in page 7"
	"* `Polygon with Points`: visualizing the polygon and the shop points from page 7"
	
	selection = st.selectbox("",('Point','Unoptimized Linestring','Optimized Linestring','Polygon','Polygon with Points'))
	
	if selection == "Point":
		queryres1 = run_query("select to_geography('POINT(-73.986226 40.755702)');")
		
		for row in queryres1:
			geojson1 = row[0]
			
		m1 = folium.Map(location=[40.755702, -73.986226], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m1)
		folium.GeoJson(geojson1, name="linestring").add_to(m1)
		st_data1 = st_folium(m1, width = 725)
		
	elif selection == "Unoptimized Linestring":
		queryres2 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'alcohol' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1)) select st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)'))			as linestring from locations;")
		
		for row in queryres2:
			geojson2 = row[0]
			
		m2 = folium.Map(location=[40.755702, -73.985144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m2)
		folium.GeoJson(geojson2, name="linestring").add_to(m2)
		st_data2 = st_folium(m2, width = 725)
		
	elif selection == "Optimized Linestring":
		queryres3 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1))select st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)')) as linestring from locations;")
		
		for row in queryres3:
			geojson3 = row[0]
			
		m3 = folium.Map(location=[40.755702, -73.984144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m3)
		folium.GeoJson(geojson3, name="linestring").add_to(m3)
		st_data3 = st_folium(m3, width = 725)
		
	elif selection == "Polygon":
		queryres4 = run_query("with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_food_beverages where shop = 'coffee' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1) union all (select fb.coordinates, st_distance(e.coordinates, fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates, fb.coordinates, 1600) where e.id = 1428036403 and fb.shop = 'alcohol' order by 2 limit 1) union all (select coordinates, st_distance(coordinates, to_geography('POINT(-73.986226 40.755702)'))::number(6, 2) as distance_meters from v_osm_ny_shop_electronics where name = 'Best Buy' and st_dwithin(coordinates, st_makepoint(-73.986226, 40.755702), 1600) = true order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates), to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations;")
		
		for row in queryres4:
			geojson4 = row[0]
			
		m4 = folium.Map(location=[40.755702, -73.984144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m4)
		folium.GeoJson(geojson4, name="linestring").add_to(m4)
		st_data4 = st_folium(m4, width = 725)	
	
	elif selection == "Polygon with Points":
		queryres5 = run_query("with final_plot as ((with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop='coffee' and st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1) union all (select fb.coordinates,st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id=1428036403 and fb.shop='alcohol' order by 2 limit 1) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name='Best Buy' and  st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) union all (with search_area as (with locations as ((select to_geography('POINT(-73.986226 40.755702)') as coordinates, 0 as distance_meters) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_food_beverages where shop='coffee' and  st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1) union all (select fb.coordinates,st_distance(e.coordinates,fb.coordinates) as distance_meters from v_osm_ny_shop_electronics e join v_osm_ny_shop_food_beverages fb on st_dwithin(e.coordinates,fb.coordinates,1600) where e.id=1428036403 and fb.shop='alcohol' order by 2 limit 1) union all (select coordinates,st_distance(coordinates,to_geography('POINT(-73.986226 40.755702)'))::number(6,2) as distance_meters from v_osm_ny_shop_electronics where name='Best Buy' and  st_dwithin(coordinates,st_makepoint(-73.986226,40.755702),1600)=true  order by 2 limit 1)) select st_makepolygon(st_makeline(st_collect(coordinates),to_geography('POINT(-73.986226 40.755702)'))) as polygon from locations) select sh.coordinates from v_osm_ny_shop sh join search_area sa on st_within(sh.coordinates,sa.polygon))) select st_collect(polygon)from final_plot;")
		
		for row in queryres5:
			geojson5 = row[0]
			
		m5 = folium.Map(location=[40.755702, -73.984144], zoom_start=16)
		folium.Marker([40.755702, -73.986226], popup="Home", tooltip="Home").add_to(m5)
		folium.GeoJson(geojson5, name="linestring").add_to(m5)
		st_data5 = st_folium(m5, width = 725)
		