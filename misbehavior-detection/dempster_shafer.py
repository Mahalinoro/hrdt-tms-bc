def adjust_bpa(r, t):
    """
    Adjust the basic probability assignment (BPA) based on the report and trust score.
    
    Parameters:
    r (int): Report from the neighboring vehicle (1 for trustworthy, 0 for untrustworthy)
    t (float): Trust score of the neighboring vehicle
    
    Returns:
    list: BPA values [m_trustworthy, m_untrustworthy, m_uncertain]
    """
    m_t = t * r
    m_u = t * (1 - r)
    m_x = 1 - t
    return [m_t, m_u, m_x]

def calculate_conflict_measure(m1_bpa, m2_bpa):
    """
    Calculate the conflict measure (K) between two BPAs.
    
    Parameters:
    m1_bpa (list): First BPA
    m2_bpa (list): Second BPA
    
    Returns:
    float: Conflict measure K
    """
    K = m1_bpa[0] * m2_bpa[1] + m1_bpa[1] * m2_bpa[0]
    return K

def combine_mass(m1_bpa, m2_bpa):
    """
    Combine two BPAs using Dempster's rule of combination.
    
    Parameters:
    m1_bpa (list): First BPA
    m2_bpa (list): Second BPA
    
    Returns:
    list: Combined BPA [m_trustworthy, m_untrustworthy, m_uncertain]
    """
    K = calculate_conflict_measure(m1_bpa, m2_bpa)
    
    if K == 1: # Readjust in case of conflict 
        # raise ValueError("Complete conflict, combination is not possible.")
        return [0, 0, 0]
    
    m_c_t = (m1_bpa[0] * m2_bpa[0] + m1_bpa[0] * m2_bpa[2] + m1_bpa[2] * m2_bpa[0]) / (1 - K)
    m_c_u = (m1_bpa[1] * m2_bpa[1] + m1_bpa[1] * m2_bpa[2] + m1_bpa[2] * m2_bpa[1]) / (1 - K)
    m_c_x = (m1_bpa[2] * m2_bpa[2]) / (1 - K)
    
    return [m_c_t, m_c_u, m_c_x]

def calculate_belief_plausibility(m):
    """
    Calculate belief and plausibility from BPA.
    
    Parameters:
    m (list): BPA values
    
    Returns:
    list: Belief and plausibility values for trustworthy and untrustworthy
    """
    bel_t = m[0]
    pl_t = 1 - m[1]
    bel_u = m[1]
    pl_u = 1 - m[0]
    return [(bel_t, pl_t), (bel_u, pl_u)]

def combine_multiple_bpas(bpas):
    """
    Combine multiple BPAs iteratively using Dempster's rule of combination.
    
    Parameters:
    bpas (list of lists): List of BPA lists from multiple neighboring vehicles
    
    Returns:
    list: Final combined BPA [m_trustworthy, m_untrustworthy, m_uncertain]
    """
    if not bpas:
        raise ValueError("No BPAs provided.")
    
    combined_mass = []
    for i in range(len(bpas)):
        if combined_mass == []:
            combined_mass.append(combine_mass(bpas[0], bpas[1]))
        else:
            new_mass = combine_mass(combined_mass[0], bpas[i])
            combined_mass[0] = new_mass
    
    return combined_mass


def dst(r_reports, t_scores, n_vehicles=5):
    bpas = []
    for i in range(n_vehicles):
        bpas.append(adjust_bpa(r_reports[i], t_scores[i]))
    
    m = combine_multiple_bpas(bpas)
    bel_pl = calculate_belief_plausibility(m[0])

    if bel_pl[0][0] > bel_pl[1][0]:
        return (bel_pl[0][0], 'trusworthy')
    else:
        return (bel_pl[0][0], 'untrustworthy')
   

# Example usage
# Example BPAs from neighboring vehicles with their respective reports and trust scores
# reports = [1, 0, 0, 1]  # Example reports from 4 neighbors
# trust_scores = [0.7, 0.2, 0.9, 0.6]  # Corresponding trust scores

# print(dst(4, reports, trust_scores))

