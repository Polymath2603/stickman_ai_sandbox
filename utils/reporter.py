class Reporter:
    @staticmethod
    def print_diagnostics(stickman):
        torso = stickman.bodies["torso"]
        l_foot = stickman.bodies["l_foot"]
        r_foot = stickman.bodies["r_foot"]
        
        print(f"--- DIAGNOSTIC REPORT (COM vs Feet) ---")
        print(f"Torso: x={torso.position.x:.2f}, y={torso.position.y:.2f}, ang={torso.angle:.2f}")
        print(f"L_Foot: x={l_foot.position.x:.2f}, y={l_foot.position.y:.2f}, ang={l_foot.angle:.2f}")
        print(f"R_Foot: x={r_foot.position.x:.2f}, y={r_foot.position.y:.2f}, ang={r_foot.angle:.2f}")
        
        print("Joint Angles:")
        for j_name, joint in stickman.joints.items():
            print(f"  {j_name}: {joint.angle:.2f}")
