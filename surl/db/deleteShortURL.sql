DELIMITER //
DROP PROCEDURE IF EXISTS deleteShortURL //
 
CREATE PROCEDURE deleteShortURL(IN target VARCHAR(2048), user VARCHAR(45))
BEGIN
    DELETE FROM urls
      WHERE short_url = target
      AND user_username = user;

      IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to delete the URL.';
      END IF;
END //
DELIMITER ;