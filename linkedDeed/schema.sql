drop table if exists stuffToPlot;
CREATE TABLE stuffToPlot(
	id integer primary key autoincrement,
	title text not null,
	description text not null
);
INSERT INTO stuffToPlot VALUES(1, 'Software developer','Java, Python, PHP');
INSERT INTO stuffToPlot VALUES(2, 'Software developer','Java, Python, PHP, SQL');
INSERT INTO stuffToPlot VALUES(3, 'Software developer','Java, Python');
INSERT INTO stuffToPlot VALUES(4, 'Software developer','Java, Python, PHP, C');
INSERT INTO stuffToPlot VALUES(5, 'Software developer','Java, Python, PHP, B');