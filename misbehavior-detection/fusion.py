def fuse_observation(t_curr, C, D):
    """
    Fuse both decisions from the Random Forest Classifier and the Dempster-Shafer Theory.
    
    Parameters:
    C (int): Classification probability provided by the Random Forest Classifier ([1,0]: close to 0 trustworthy, 1 untrustworthy)
    D (float): Probability of an event ([1,0]: close to 1 trustworthy, close 0 untrustworthy)
    
    Returns:
    list: [update_status, reward, penalty]
    """

    # Define weights and penalty w & p, threshold t
    w = {
        "W_HIGH": 0.1,
        "W_MODERATE": 0.05,
        "W_LOW": 0.02,
    }

    p = {
        "P_HIGH": -0.1,
        "P_MODERATE": -0.05,
        "P_LOW": -0.02
    }

    t = {
        "T_HIGH": 0.7,
        "T_LOW": 0.3
    }

    # Decide based on the classification and the result from DST
    if D[0] >= t["T_HIGH"]:
        if C == 0:
            t_new = t_curr + w["W_HIGH"]
        else:
            t_new = t_curr + p["P_LOW"]
        
    elif t["T_LOW"] < D[0] < t["T_HIGH"]:
        if C == 0:
            t_new = t_curr + w['W_LOW']
        else:
            t_new = t_curr + p["P_MODERATE"]
        
    else:
        if C == 0:
            t_new = t_curr + p["P_MODERATE"]
        else:
            t_new = t_curr + p["P_HIGH"]
    
    t_new = max(0, min(1, t_new))

    return t_new
        
# print(fuse_observation())
