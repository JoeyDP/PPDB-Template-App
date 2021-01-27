CREATE TABLE Quote(
	id SERIAL PRIMARY KEY,
	text VARCHAR(256) UNIQUE NOT NULL,
	author VARCHAR(128)
);

INSERT INTO Quote(text,author) VALUES('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.','John Louis von Neumann');
INSERT INTO Quote(text,author) VALUES('The choice you refuse to make, is the one that will be made for you.', 'Unknown');
INSERT INTO Quote(text,author) VALUES('Computer science is no more about computers than astronomy is about telescopes.','Edsger Dijkstra');
INSERT INTO Quote(text,author) VALUES('You look at things that are and ask, why? I dream of things that never were and ask, why not?','Unknown');
INSERT INTO Quote(text,author) VALUES('Being efficient is also a form of perfection.', 'Joey');
INSERT INTO Quote(text,author) VALUES('To understand recursion you must first understand recursion..', 'Unknown');
INSERT INTO Quote(text,author) VALUES('Not everyone will understand your journey. Thats fine. Its not their journey to make sense of. Its yours.','Unknown');
INSERT INTO Quote(text,author) VALUES('One must have enough self-confidence and immunity to peer pressure to break the grip of standard paradigms.', 'Marvin Minsky');
INSERT INTO Quote(text,author) VALUES('Everyone you meet is fighting a battle you know nothing about. Be kind. Always.', 'Robin Williams');
INSERT INTO Quote(text,author) VALUES('[...] it is usual to have the polite convention that everyone thinks.', 'Alan Turing');
