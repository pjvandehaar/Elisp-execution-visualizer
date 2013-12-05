(defun lose_head (str start)
  (if (= 0 start)
      str
    (lose_head
     (substring str 1)
     (- start 1))))
(lose_head "a s df" 2)
