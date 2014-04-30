(defvar m5k-py-path "/usr/bin/env python /path/to/m5k.py")
(defvar m5k-py-engine "vlc")

(defun m5k-play ()
  "Play m5k files"
  (interactive)
  (if buffer-file-name
      (progn
        (setq is-m5k-file (numberp (string-match "\.m5k$" buffer-file-name)))
        (if is-m5k-file
            (progn
              (setq cmd (concat (getenv "B") m5k-py-path " -l -e " m5k-py-engine " -ff "))
              (shell-command (concat cmd buffer-file-name))
              (message "Playing %s" buffer-file-name))))))

(defun m5k-kill ()
  "Kill m5k files"
  (interactive)
  (if buffer-file-name
      (progn
        (setq is-m5k-file (numberp (string-match "\.m5k$" buffer-file-name)))
        (if is-m5k-file
            (progn
              (setq cmd (concat (getenv "B") m5k-py-path " -k -ff "))
              (shell-command (concat cmd buffer-file-name))
              (message "Killing %s" buffer-file-name))))))

(global-set-key '[?\C-c ?\C-k]  `m5k-kill)
(global-set-key '[?\C-c ?\C-r]  `m5k-play)

(provide 'm5k-mode)
