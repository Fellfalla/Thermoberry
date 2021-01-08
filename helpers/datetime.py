def in_between(now, start, end):
    """
    Source: https://stackoverflow.com/a/33681543/5006592
    """
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end