-- 1. What are the 10 most downloaded apps of all time?
select top 10 App, Category, Installs, Rating
from MainApps
order by Installs DESC;
-----------------------------------------------------------
-- 2. Which category has the highest average rating?
select top 1 Category,CAST(ROUND(AVG(Rating), 2) AS DECIMAL(10,2)) AS Avg_Rating
from MainApps
group by Category
order by Avg_Rating DESC;
------------------------------------------------------------
-- 3. Which category has the most total downloads?
select top 1 Category, SUM(Installs) AS Total_Downloads
from MainApps
group by Category
order by Total_Downloads DESC;
------------------------------------------------------------
-- 4. Do paid apps have better ratings than free apps?
select Type, CAST(ROUND(AVG(Rating), 2) AS DECIMAL(10,2)) AS Avg_Rating, COUNT(*) AS App_Count
from MainApps
group by Type
order by Avg_Rating DESC;
------------------------------------------------------------
-- 5. Do paid apps or free apps get more downloads?
select Type,FORMAT(SUM(Installs), 'N0') AS Total_Downloads
from MainApps
group by Type
order by SUM(Installs) DESC;        
------------------------------------------------------------
-- 6. What is the most common price for paid apps?
select top 3 Price, COUNT(*) AS Number_of_Apps
from MainApps
where Type = 'Paid' AND Price > 0
group by Price
order by Number_of_Apps DESC;
------------------------------------------------------------
-- 7. Do smaller apps get more downloads or better ratings?
select Size_Group,
       Avg_Downloads,
       Avg_Rating,
       RANK() OVER (ORDER BY Avg_Downloads DESC) AS Download_Rank,
       RANK() OVER (ORDER BY Avg_Rating DESC) AS Rating_Rank
from (
    select 
        CASE 
            WHEN Size_MB < 20 THEN 'Small (<20MB)'
            WHEN Size_MB < 50 THEN 'Medium (20-50MB)'
            ELSE 'Large (>=50MB)'
        END AS Size_Group,
        FORMAT(AVG(Installs) , 'N0') AS Avg_Downloads, 
        CAST(ROUND(AVG(Rating), 2) AS DECIMAL(10,2)) AS Avg_Rating
    from MainApps
    group by 
        CASE 
            WHEN Size_MB < 20 THEN 'Small (<20MB)'
            WHEN Size_MB < 50 THEN 'Medium (20-50MB)'
            ELSE 'Large (>=50MB)'
        END
) t;
-------------------------------------------------------------------
-- 8. Do apps that support older Android versions get more downloads?
select Android_Group,
       Total_Downloads,
       App_Count,
       RANK() OVER (order by Total_Downloads desc) AS Reach_Rank
from (
    select 
        CASE 
            WHEN Android_Min_Version < 4.0 THEN 'Very Old (<4.0)'
            WHEN Android_Min_Version < 5.0 THEN 'Old (4.0–4.9)'
            ELSE 'Modern (5.0+)'
        END AS Android_Group,
        FORMAT(SUM(Installs), 'N0') AS Total_Downloads,
        COUNT(*) AS App_Count
    from MainApps
    group by 
        CASE 
            WHEN Android_Min_Version < 4.0 THEN 'Very Old (<4.0)'
            WHEN Android_Min_Version < 5.0 THEN 'Old (4.0–4.9)'
            ELSE 'Modern (5.0+)'
        END
) t;
-----------------------------------------------------------------------
-- 9. Which categories have the happiest users (highest sentiment polarity)?
select Category, Avg_Sentiment, Happiness_Rank
from (
    select m.Category,
           AVG(r.Sentiment_Polarity) AS Avg_Sentiment,
           ROW_NUMBER() OVER (ORDER BY AVG(r.Sentiment_Polarity) DESC) AS Happiness_Rank
    from MainApps m
     join UserReviews r on m.App = r.App
    group by m.Category
) t
order by Happiness_Rank;
-------------------------------------------------------------------------
-- 10. Which genres are the real hidden winners (high rating + high installs)?
select top 20 
    Genre,
    App_Count,
    Avg_Rating,
    FORMAT(Total_Downloads, 'N0') AS Total_Downloads,
    Success_Score,
    ROW_NUMBER() OVER (ORDER BY Success_Score DESC) AS Final_Rank
from (
    select 
        Genres AS Genre,
        COUNT(*) AS App_Count,
        CAST(ROUND(AVG(Rating), 2) AS DECIMAL(10,2)) AS Avg_Rating,
        SUM(Installs) AS Total_Downloads,
        -- logic of success score: 50% rating + 50% downloads, Keep installs on same scale as ratings by dividing by 1B.
        cast(ROUND((AVG(Rating) * 1.0) + (SUM(Installs) / 1000000000.0) , 2) AS DECIMAL(10,2)) AS Success_Score
    from MainApps
    group by Genres
) t
order by Final_Rank;
-----------------------------------------------------------------------
-- 11. Which paid apps make the most money (Price × Installs)?
select App, Category, Price, Installs, Estimated_Revenue
from (
    select App, Category, Price, format(Installs , 'N0') as Installs,
           format((Price * Installs) , 'N0') AS Estimated_Revenue,
           ROW_NUMBER() OVER (ORDER BY Price * Installs DESC) AS Revenue_Rank
    from MainApps
    where Type = 'Paid' AND Price > 0
) t
where Revenue_Rank <= 10;
-------------------------------------------------------------------------
