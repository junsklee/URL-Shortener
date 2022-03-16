DROP TABLE IF EXISTS urls;
CREATE TABLE urls (
  id INT NOT NULL AUTO_INCREMENT,
  long_url varchar(2048) NOT NULL,
  short_url varchar(2048) NOT NULL,
  user_username varchar(45),
  PRIMARY KEY (id),
  FOREIGN KEY (user_username) REFERENCES users(user)
);