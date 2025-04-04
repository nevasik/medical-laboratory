QUERIES = {
    'check_admin': """
        SELECT 'Администратор', NULL, 'images/Администратор.png', login 
        FROM administrators 
        WHERE login = %s AND password = %s
    """,
    'check_lab_technician': """
        SELECT 
            CASE WHEN is_researcher THEN 'Лаборант-исследователь' ELSE 'Лаборант' END,
            full_name,
            CASE WHEN is_researcher THEN 'images/laborant_2.png' ELSE 'images/laborant_1.jpeg' END,
            login 
        FROM lab_technicians 
        WHERE login = %s AND password = %s
    """,
    'check_accountant': """
        SELECT 'Бухгалтер', full_name, 'images/Бухгалтер.jpeg', login 
        FROM accountants 
        WHERE login = %s AND password = %s
    """,
    'log_login': """
        INSERT INTO login_history (login, success, attempt_time, role)
        VALUES (%s, %s, NOW(), %s)
    """,
    'get_history': """
        SELECT attempt_time, login, success, role 
        FROM login_history
        WHERE login LIKE %s
        ORDER BY attempt_time {sort_order}
    """
}