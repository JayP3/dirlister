select * from dir_listing where filepath LIKE 'C:\Users\Jay\Downloads%';

select filepath, count(filepath) as num from dir_listing  group by filepath order by num desc;

select count(id)  from dir_listing;