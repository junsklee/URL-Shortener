DELIMITER //
DROP PROCEDURE IF EXISTS addURL //
 
CREATE PROCEDURE addURL (IN inURL VARCHAR(2048), IN userIn varchar(45))
BEGIN
  IF(SELECT EXISTS(SELECT * FROM users WHERE user = userIn) < 1) THEN
    CALL addUser(userIn);
  END IF;
  
  INSERT INTO urls (long_url, short_url, user_username) VALUES(
	inURL,
	SUBSTR(MD5(RAND()), 1, 5),
  userIn);

  IF(ROW_COUNT() = 0) THEN
    SIGNAL SQLSTATE '52711'
    SET MESSAGE_TEXT = 'Unable to add the URL.';
  END IF;

  /*SELECT LAST_INSERT_ID();*/
  SELECT * FROM urls
  WHERE id = LAST_INSERT_ID();
  
END //
DELIMITER ;