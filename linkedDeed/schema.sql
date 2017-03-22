drop table if exists stuffToPlot;
drop table if exists linkedIn;
CREATE TABLE linkedIn(
	ID integer primary key autoincrement,
	EMAIL text,
	PASSWORD text,
	WHAT text,
	CITY text,
	STATE text,
	SKILLS text
);
