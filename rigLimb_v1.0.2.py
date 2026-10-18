"""
RIG LIMB SCRIPT V.1.0.2
Created by Alva Stenhammar

Automatically rig limbs. Only works limbs with three joints (basically biped rigs).

"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
import functools



def _______________UI_______________(): pass


def insertSeparator(parent: str):
    """ Create custom separator. """

    cmds.separator(height=2,
                  style="none",
                  backgroundColor=(0.2, 0.2, 0.2),
                  parent=parent)



def createColumnLayout(parent: str) -> str:
    """
    Create row/column layout with custom settings.

    Return layout's full path name.
    """

    layout = cmds.rowColumnLayout(numberOfColumns=2,
                                  columnWidth=[(1, 130), (2, 130)],
                                  columnOffset=[(1, "right", 10), (2, "left", 10)],
                                  rowSpacing=(1, 5),
                                  parent=parent)
    
    return cmds.rowColumnLayout(layout, query=True, fullPathName=True)



def createFrameLayout(label: str, parent: str) -> str:
    """
    Create frame layout layout with custom settings.

    Return layout's full path name.
    """

    layout = cmds.frameLayout(label=label,
                              width=300,
                              marginWidth=20,
                              marginHeight=10,
                              backgroundShade=True,
                              font="boldLabelFont",
                              parent=parent)
    
    return cmds.frameLayout(layout, query=True, fullPathName=True)



def createButton(label: str, parent: str) -> str:
    """
    Create button with custom settings.
    
    Return button's full path name.
    """

    cmds.rowLayout(numberOfColumns=1,
                   columnWidth=(1, 260),
                   parent=parent)
    
    button = cmds.button(label=label,
                         width=260)
    
    return cmds.button(button, query=True, fullPathName=True)



def createUI(buildLimbRig):
    """ Create and open the UI. """


    # WINDOW CREATION
    windowID = "rigLimbWindowID"
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    cmds.window(windowID, title=f"Rig Limb", sizeable=True)


    # LAYOUTS
    mainLayout = cmds.columnLayout(width=310, margins=5)

    cmds.columnLayout(margins=10,
                      parent=mainLayout)
    cmds.text(label="Rig Limb Tool",
              width=280,
              font="boldLabelFont")
    cmds.separator(height=10, style="none")


    # LAYOUT SETUP
    layout = createFrameLayout("Options", mainLayout)
    cmds.separator(height=5, style="none", parent=mainLayout)
    
    cmds.text(label="Select shoulder or hip joint to rig.",
                width=260, height=10,
                font="smallPlainLabelFont")
    insertSeparator(layout)

    cmds.separator(height=5, style="none", parent=mainLayout)


    # LAYOUT

    createColumnLayout(parent=layout)
    
    cmds.text("Limb type:")
    limbTypeMenu = cmds.optionMenu()
    cmds.menuItem(label="Arm")
    cmds.menuItem(label="Leg")

    cmds.text(label="Global scale:")
    globalScaleField = cmds.floatField(value=10, precision=2, width=50)

    cmds.text(label="Stretchy limb:")
    stretchBox = cmds.checkBox(label="", value=True)

    # apply button
    cmds.separator(height=1, style="none", enableBackground=False, parent=layout)
    applyButton = createButton("Rig Limb", layout)


    # CREDITS TEXT
    cmds.columnLayout(margins=10,
                        parent=mainLayout)
    
    cmds.separator(height=5,
                    style="none")
    
    cmds.text(label="Created by Alva Stenhammar", width=280,
                font="obliqueLabelFont")
    

    # ADD COMMANDS
    # apply button
    cmds.button(applyButton, edit=True,
                command=functools.partial(buildLimbRig,
                                          limbTypeMenu,
                                          globalScaleField,
                                          stretchBox))


    cmds.showWindow()
    

def _______________GENERIC_______________(): pass


def transferTransformsToOPM(node: str):
    """ Transfer object's transform to the Offset Parent Matrix then clear the object's transforms. """

    localMatrix = om.MMatrix(cmds.xform(node, q=True, m=True, ws=False))
    offsetParentMatrix = om.MMatrix(cmds.getAttr(f"{node}.offsetParentMatrix"))
    newMatrix = localMatrix * offsetParentMatrix

    cmds.setAttr(f"{node}.offsetParentMatrix", newMatrix, type="matrix")

    # attributes to clear, add jointOrient if attr exists (for joints)
    transformList = [".translate", ".rotate", ".scale",]
    transformList.append(".jointOrient") if cmds.attributeQuery('jointOrient', node=node, exists=True) else False

    # reset transform values
    for attribute in transformList:
        value = 1 if attribute == ".scale" else 0
        for axis in ["X", "Y", "Z"]:
            cmds.setAttr(node + attribute + axis, value)



def isParentOf(parent: str,
               child: str) -> bool:
    """ Check if the first object is a parent of the second object. """

    childParent = cmds.listRelatives(child, parent=True)

    if childParent == None:
        return False
    elif childParent[0] == parent:
        return True
    else:
        return False



def _______________CREATE_______________(): pass


def createControl(name: str,
                  shape: str,
                  size: float) -> tuple[str]:
    """
    Create a control with different shapes.

    Return name of control and offset group.

    Control shapes:
    - circle
    - locator
    - pyramid
    - box
    - arrows
    - plus
    - star
    """

    if shape == "circle":
        control = cmds.circle(name=name, normal=(0, 1, 0))[0]


    elif shape == "locator":
        # curve1 = cmds.curve(point=[[1, 0, 0], [-1, 0, 0]], degree=1)
        # curve2 = cmds.curve(point=[[0, 1, 0], [0, -1, 0]], degree=1)
        # curve3 = cmds.curve(point=[[0, 0, 1], [0, 0, -1]], degree=1)

        # for i, curve in enumerate([curve1, curve2, curve3]):
        #     cmds.rename(curve, f"tempCurve{i+1}")

        # for i in range(3):            
        #     if i != 0:
        #         cmds.parent(f"tempCurveShape{i+1}", "tempCurve1", relative=True, shape=True)
        #         cmds.delete(f"tempCurve{i+1}")

        # control = cmds.rename("tempCurve1", name)

        control = cmds.spaceLocator(name=name)[0]

        for axis in ["X", "Y", "Z"]:
            cmds.setAttr(f"{control}.localScale{axis}", size)


    elif shape == "pyramid":
        positionList = [[1, 1, 1], [1, 1, -1], [-1, 1, -1], [-1, 1, 1], [1, 1, 1],
                        [0, 0, 0], [-1, 1, -1], [1, 1, -1], [0, 0, 0], [-1, 1, 1]]

        control = cmds.curve(name=name, point=positionList, degree=1)
        cmds.closeCurve(control, replaceOriginal=True)
        cmds.scale(1, 2, 1, control)

        # get shape node and rename because it won't do it automatically for some reason ._.
        shapeNode = cmds.listRelatives(control, shapes=True)[0]
        cmds.rename(shapeNode, f"{control}Shape")


    elif shape == "box":
        cmds.select(clear=True)
        curve1 = cmds.curve(point=[[1, 1, 1], [1, 1, -1], [-1, 1, -1], [-1, 1, 1]], degree=1)
        cmds.closeCurve(curve1, replaceOriginal=True)
        curve2 = cmds.curve(point=[[1, -1, 1], [1, -1, -1], [-1, -1, -1], [-1, -1, 1]], degree=1)
        cmds.closeCurve(curve2, replaceOriginal=True)

        curve3 = cmds.curve(point=[[1, 1, 1], [1, -1, 1]], degree=1)
        curve4 = cmds.curve(point=[[1, 1, -1], [1, -1, -1]], degree=1)
        curve5 = cmds.curve(point=[[-1, 1, 1], [-1, -1, 1]], degree=1)
        curve6 = cmds.curve(point=[[-1, 1, -1], [-1, -1, -1]], degree=1)

        for i, curve in enumerate([curve1, curve2, curve3, curve4, curve5, curve6]):
            cmds.rename(curve, f"tempCurve{i+1}")

        for i in range(6):            
            if i != 0:
                cmds.parent(f"tempCurveShape{i+1}", "tempCurve1", relative=True, shape=True)
                cmds.delete(f"tempCurve{i+1}")

        control = cmds.rename("tempCurve1", name)


    elif shape == "arrows":
        positionList = [[0, 0, -5], [2, 0, -3], [1, 0, -3], [1.8, 0, -1.8],
                        [3, 0, -1], [3, 0, -2], [5, 0, 0], [3, 0, 2], [3, 0, 1],
                        [1.8, 0, 1.8], [1, 0, 3], [2, 0, 3], [0, 0, 5], [-2, 0, 3],
                        [-1, 0, 3], [-1.8, 0, 1.8], [-3, 0, 1], [-3, 0, 2], [-5, 0, 0],
                        [-3, 0, -2], [-3, 0, -1], [-1.8, 0, -1.8], [-1, 0, -3], [-2, 0, -3]]

        control = cmds.curve(name=name, point=positionList, degree=1)
        cmds.closeCurve(control, replaceOriginal=True)


    elif shape == "plus":
            positions = [[-1, 5, 0], [1, 5, 0], [1, 1, 0], [5, 1, 0], [5, -1, 0],
                        [1, -1, 0], [1, -5, 0], [-1, -5, 0], [-1, -1, 0], [-5, -1, 0],
                        [-5, 1, 0], [-1, 1, 0], [-1, 5, 0]]
            
            control = cmds.curve(name=name, degree=1, point=positions)
            cmds.select(control)
            cmds.scale(size * 0.1, size * 0.1, size * 0.1)
            cmds.select(clear=True)
            cmds.makeIdentity(control, apply=True, scale=True)

    
    elif shape == "star":
        control = cmds.circle(name=name, radius=(size * 1.3), sections=16)[0]
        
        count = 0

        for i in range(16):
            if count % 2 == 0:
                cmds.select(f"{control}.cv[{str(i)}]", add=True)
            count += 1
        
        cmds.scale(0.7, 0.7, 0.7)
        cmds.select(clear=True)


    # scale to size
    cmds.scale(size, size, size, control, relative=True, objectSpace=True)
    cmds.makeIdentity(control, apply=True, scale=True)

    # add offset group
    group = cmds.group(control, name=control.replace("CTRL", "GRP"))

    cmds.select(clear=True)

    return (control, group)



def createFK(limb: str,
             jointChain: list[str],
             controlGroup: str,
             globalScale: float,
             IKFKgroup: str):
    """ Create FK setup with existing controls. If no controls exist, create basic ones. """

    fkControls = []

    # create joints
    for bindJoint in jointChain:
        newJoint = bindJoint.replace("BIND", "FK")

        cmds.joint(name=newJoint, radius=0.5)
        cmds.matchTransform(newJoint, bindJoint)
        cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

    cmds.select(clear=True)


    for i, bindJoint in enumerate(jointChain):
        controlName = bindJoint.replace("BIND_JNT", "FK_CTRL")

        # create control if one doesn't exist
        if not cmds.objExists(controlName):
            control, group = createControl(name=controlName, shape="circle", size=(1 * globalScale))

        # move to bind joint and transfer transforms
        cmds.matchTransform(group, bindJoint)
        transferTransformsToOPM(group)

        # fix rotation
        cmds.setAttr(f"{control}.rotateX", 180)
        cmds.makeIdentity(control, apply=True, rotate=True)

        # parent bind joint to control
        cmds.parentConstraint(control, bindJoint.replace("BIND", "FK"), maintainOffset=True)

        fkControls.append(control)

        # parent to previous control
        if i != 0:
            cmds.parent(group, fkControls[i-1])

    # fix hierarchy
    cmds.parent(fkControls[0].replace("CTRL", "GRP"), controlGroup)
    cmds.parent(jointChain[0].replace("BIND", "FK"), IKFKgroup)


    # add ankle locator at fk joint position and parent to fk ankle ctrl to help with matching ik to fk
    if limb[2:] == "leg":
        ankleLocator = cmds.spaceLocator(name=jointChain[2].replace("BIND_JNT", "LOC"))[0]
        cmds.matchTransform(ankleLocator, jointChain[2], position=True, rotation=False)
        cmds.parent(ankleLocator, jointChain[2].replace("BIND_JNT", "FK_CTRL"))
        cmds.setAttr(f"{ankleLocator}.visibility", 0)
    
        
    cmds.select(clear=True)



def createIK(limb: str,
             jointChain: list[str],
             controlGroup: str,
             globalScale: float,
             IKFKgroup: str):
    """ Create the IK handles and pole vector with existing controls. """

    ikControl = f"{limb}_IK_CTRL"
    ikGroup = f"{limb}_IK_GRP"
    pvControl = f"{limb}_PV_CTRL"
    pvGroup = f"{limb}_PV_GRP"
    ikJoints = []

    # create joints
    for bindJoint in jointChain:
        newJoint = bindJoint.replace("BIND", "IK")
        ikJoints.append(newJoint)

        cmds.joint(name=newJoint, radius=0.5)
        cmds.matchTransform(newJoint, bindJoint)
        cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

    cmds.select(clear=True)

    # set preferred angle
    for joint in ikJoints:
        currentRotation = cmds.xform(joint, query=True, rotation=True, worldSpace=False)
        for i, axis in enumerate(["X", "Y", "Z"]):
            cmds.setAttr(f'{joint}.preferredAngle{axis}', currentRotation[i])


    # create controls if they don't exist
    if not cmds.objExists(ikControl):
        ikControl, ikGroup = createControl(name=ikControl, shape="box", size=(1 * globalScale))
        cmds.matchTransform(ikGroup, jointChain[2])

        if limb.split("_")[1] == "leg":
            for axis in ["X", "Y", "Z"]:
                cmds.setAttr(f"{ikGroup}.rotate{axis}", 0)

        transferTransformsToOPM(ikGroup)

    if not cmds.objExists(pvControl):
        pvControl, pvGroup = createControl(name=pvControl, shape="pyramid", size=(0.2 * globalScale))

        cmds.setAttr(f"{pvControl}.rotateX", -90)
        cmds.makeIdentity(pvControl, apply=True)

        # move PV to correct location (polygon method)
        
        # get list of joint positions
        pointList = []
    
        for joint in jointChain:
            position = cmds.xform(joint, query=True, worldSpace=True, translation=True)
            pointList.append(position)
    
        polySurface = cmds.polyCreateFacet(point=pointList, constructionHistory=False)[0]
    
        # centre pivot
        centre = cmds.objectCenter(polySurface)
        midVertex = cmds.xform(f"{polySurface}.vtx[1]", query=True, worldSpace=True, translation=True)
    
        cmds.move(centre[0], centre[1], centre[2], f"{polySurface}.scalePivot", f"{polySurface}.rotatePivot")
    
        # scale surface
        cmds.scale(2 * globalScale, 2 * globalScale, 2 * globalScale, polySurface)
    
        # get pv position and move pv to it
        pvPosition = cmds.xform(f"{polySurface}.vtx[1]", query=True, worldSpace=True, translation=True)
        cmds.move(pvPosition[0], pvPosition[1], pvPosition[2], pvGroup)
    
        # delete temp poly surface
        cmds.delete(polySurface)
    
        # move translate values to offset parent matrix
        transferTransformsToOPM(pvGroup)


    # create IK handle and parent to correct control
    cmds.ikHandle(name=f"{limb}_HNDL",
                  solver="ikRPsolver",
                  startJoint=jointChain[0].replace("BIND", "IK"),
                  endEffector=jointChain[2].replace("BIND", "IK"))
    cmds.parent(f"{limb}_HNDL", ikControl)

    # hide IK handle
    cmds.setAttr(f"{limb}_HNDL.visibility", 0)

    # add orient constraint for wrist control
    cmds.orientConstraint(ikControl, jointChain[2].replace("BIND", "IK"))


    # POLE VECTOR

    # add PV constraint
    cmds.poleVectorConstraint(pvControl, f"{limb}_HNDL")


    # POLE VECTOR OFFSET

    # create follow attribute
    cmds.select(pvControl)
    cmds.addAttr(attributeType="float",
                    hasMaxValue=True, hasMinValue=True,
                    maxValue=1, minValue=0,
                    longName="follow",
                    niceName="Follow")
    cmds.setAttr(f"{pvControl}.follow", keyable=True)
    cmds.setAttr(f"{pvControl}.follow", 1)
    cmds.select(clear=True)

    # create world space locator
    wsLocator = "worldSpace_LOC"
    if not cmds.objExists(wsLocator):
        cmds.spaceLocator(name=wsLocator)
    
    # pole vector offset setup
    offsetParent = cmds.spaceLocator(name=f"{limb}_PV_offsetParent")[0]
    upObject = cmds.spaceLocator(name=f"{limb}_PV_aim_upObject")[0]

    cmds.matchTransform(upObject, jointChain[0].replace("BIND", "IK"), position=True, rotation=False)

    cmds.move(0, 0, (10 * globalScale), upObject,
                relative=True, objectSpace=True, worldSpaceDistance=True)

    cmds.pointConstraint(jointChain[0].replace("BIND", "IK"), offsetParent)
    cmds.aimConstraint(ikControl, offsetParent,
                       aim=(1, 0, 0), upVector=(0, 1, 0),
                       maintainOffset=True,
                       worldUpType="object",
                       worldUpObject=upObject)
    
    pvConstraint = cmds.parentConstraint(wsLocator, offsetParent, pvGroup, maintainOffset=True)[0]
    reverseNode = cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_PV_follow_reverse")

    cmds.connectAttr(f"{pvControl}.follow", f"{reverseNode}.inputX")
    cmds.connectAttr(f"{reverseNode}.outputX", f"{pvConstraint}.{wsLocator}W0")
    cmds.connectAttr(f"{pvControl}.follow", f"{pvConstraint}.{offsetParent}W1")


    # add PV annotation arrow
    pvArrow = f"{limb}_PV_ARROW"
    annotationShape = cmds.createNode("annotationShape", name=f"{pvArrow}Shape")

    cmds.connectAttr(f"{limb}_PV_CTRLShape.worldMatrix[0]",
                        f"{annotationShape}.dagObjectMatrix[0]")

    cmds.matchTransform(pvArrow, f"{jointChain[1].replace("BIND", "IK")}")
    cmds.parentConstraint(f"{jointChain[1].replace("BIND", "IK")}", pvArrow, maintainOffset=True)


    # add pv locator at pv position and parent to fk elbow ctrl to help with matching ik to fk
    pvLocator = cmds.spaceLocator(name=jointChain[1].replace("BIND_JNT", "PV_LOC"))[0]
    cmds.matchTransform(pvLocator, pvControl)
    cmds.parent(pvLocator, jointChain[1].replace("BIND_JNT", "FK_CTRL"))
    cmds.setAttr(f"{pvLocator}.visibility", 0)


    # parent constrain ik root joint to chest/cog control if they exist
    if limb[2:] == "arm" and cmds.objExists("C_chest_CTRL"):
        cmds.parentConstraint("C_chest_CTRL", ikJoints[0], maintainOffset=True)

    if limb[2:] == "leg" and cmds.objExists("C_cog_CTRL"):
        cmds.parentConstraint("C_cog_CTRL", ikJoints[0], maintainOffset=True)

    
    # fix hierarchy
    cmds.parent(ikJoints[0], IKFKgroup)

    cmds.parent(ikGroup, controlGroup)
    cmds.parent(pvGroup, controlGroup)

    cmds.parent(pvArrow, pvGroup)
    
    cmds.parent(offsetParent, f"{limb}_IKFK")
    cmds.parent(upObject, f"{limb}_IKFK")

    cmds.select(clear=True)



def createIKFKswitch(limb: str,
                     jointChain: list,
                     IKFKgroup: str) -> list[str]:
    """
    Create the switch between FK and IK joints, then connect it to the IK/FK switch attribute.
    
    Return list of created attributes.
    """

    # ATTRIBUTES
    # create switch group
    IKFKswitch = cmds.group(empty=True, name=f"{limb}_IKFK_switch")
    cmds.parent(IKFKswitch, IKFKgroup)
        
    # add attribute divider to switch group ——————————
    cmds.select(IKFKswitch)
    cmds.addAttr(attributeType="enum",
                    longName="attributeDivider",
                    niceName="###############",
                    enumName="IK/FK")
    cmds.setAttr(f"{IKFKswitch}.attributeDivider", channelBox=True)
    cmds.select(clear=True)

    # add IK/FK switch attribute
    cmds.select(IKFKswitch)
    cmds.addAttr(attributeType="float",
                    hasMaxValue=True, hasMinValue=True,
                    maxValue=1, minValue=0,
                    longName="IKFKswitch",
                    niceName="IK/FK Switch")
    cmds.setAttr(f"{IKFKswitch}.IKFKswitch", keyable=True)
    cmds.setAttr(f"{IKFKswitch}.IKFKswitch", 1)
    cmds.select(clear=True)

    
    # reverse node
    cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_IKFK_reverse")
    cmds.connectAttr(f"{IKFKswitch}.IKFKswitch",
                     f"{limb}_IKFK_reverse.inputX",
                     force=True)

    for i, bindJoint in enumerate(jointChain):
        # get joint name by removing BIND_JNT
        jointName = "_".join(bindJoint.split("_")[:-2])

        # create FK and IK joint names
        FKjoint = f"{jointName}_FK_JNT"
        IKjoint = f"{jointName}_IK_JNT"

        cmds.parentConstraint(FKjoint, IKjoint, bindJoint, maintainOffset=False)

        # connect switch attribute
        getConstraint = cmds.listConnections(jointChain[i], type="parentConstraint")[0]
        getWeights = cmds.parentConstraint(getConstraint, query=True, weightAliasList=True)

        cmds.connectAttr(f"{IKFKswitch}.IKFKswitch",
                         f"{getConstraint}.{getWeights[0]}",
                         force=True)
        cmds.connectAttr(f"{limb}_IKFK_reverse.outputX",
                         f"{getConstraint}.{getWeights[1]}",
                         force=True)

    return ["attributeDivider", "IKFKswitch"]



def createStretch(limb: str,
                  jointChain: list[str]) -> list[str]:
    """
    Add stretch to IK limb with options for stretchiness and stretch type.
    
    Return list of created attributes.
    """

    ikControl = f"{limb}_IK_CTRL"
    IKFKswitch = f"{limb}_IKFK_switch"
    stretchJointList = []

    # create stretch joints
    for bindJoint in jointChain:
        newJoint = bindJoint.replace("BIND", "STRETCH")

        cmds.joint(name=newJoint, radius=0.5)
        cmds.matchTransform(newJoint, bindJoint)
        cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

        stretchJointList.append(newJoint)

    cmds.select(clear=True)

    # parent constrain stretch root joint to chest/cog control if they exist
    if limb[2:] == "arm" and cmds.objExists("C_chest_CTRL"):
        cmds.parentConstraint("C_chest_CTRL", stretchJointList[0], maintainOffset=True)

    if limb[2:] == "leg" and cmds.objExists("C_cog_CTRL"):
        cmds.parentConstraint("C_cog_CTRL", stretchJointList[0], maintainOffset=True)


    # create end position locator, move to end joint, and parent to end joint control
    cmds.spaceLocator(name=f"{limb}_endPos_LOC")
    cmds.matchTransform(f"{limb}_endPos_LOC", jointChain[2])
    cmds.parent(f"{limb}_endPos_LOC", ikControl)

    # hide locator
    cmds.setAttr(f"{limb}_endPos_LOC.visibility", 0)

    # build distance nodes for each section (but skip finger/toe joints)
    cmds.shadingNode("plusMinusAverage", asUtility=True, name=(limb + "_length"))

    for i in range(2):
            cmds.shadingNode("distanceBetween", asUtility=True, name=f"{stretchJointList[i]}_distnode")

            cmds.connectAttr(f"{stretchJointList[i]}.worldMatrix",
                             f"{stretchJointList[i]}_distnode.inMatrix1",
                             force=True)
            cmds.connectAttr(f"{stretchJointList[i+1]}.worldMatrix",
                             f"{stretchJointList[i]}_distnode.inMatrix2",
                             force=True)
            
            cmds.connectAttr(f"{stretchJointList[i]}.rotatePivotTranslate",
                             f"{stretchJointList[i]}_distnode.point1",
                             force=True)
            cmds.connectAttr(f"{stretchJointList[i+1]}.rotatePivotTranslate",
                             f"{stretchJointList[i]}_distnode.point2",
                             force=True)
            
            cmds.connectAttr(f"{stretchJointList[i]}_distnode.distance",
                             f"{limb}_length.input1D[{str(i)}]",
                             force=True)

    # get distance from root to stretch end locator
    cmds.shadingNode("distanceBetween", asUtility=True, name=f"{limb}_STRETCH_distnode")

    cmds.connectAttr(f"{stretchJointList[0]}.worldMatrix",
                     f"{limb}_STRETCH_distnode.inMatrix1",
                     force=True)
    cmds.connectAttr(f"{limb}_endPos_LOC.worldMatrix",
                     f"{limb}_STRETCH_distnode.inMatrix2",
                     force=True)
    
    cmds.connectAttr(f"{stretchJointList[0]}.rotatePivotTranslate",
                     f"{limb}_STRETCH_distnode.point1",
                     force=True)
    cmds.connectAttr(f"{limb}_endPos_LOC.rotatePivotTranslate",
                     f"{limb}_STRETCH_distnode.point2",
                     force=True)
    
    # create nodes to check for and control stretching
    cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{limb}_scaleFactor")
    cmds.shadingNode("condition", asUtility=True, name=f"{limb}_condition")

    # adjust node settings
    cmds.setAttr(f"{limb}_scaleFactor.operation", 2)
    cmds.setAttr(f"{limb}_condition.operation", 2)
    cmds.setAttr(f"{limb}_condition.secondTerm", 1)

    # connect stretch distance to scale factor
    cmds.connectAttr(f"{limb}_STRETCH_distnode.distance",
                     f"{limb}_scaleFactor.input1X",
                     force=True)
    
    # connect leg distance to scale factor
    cmds.connectAttr(f"{limb}_length.output1D",
                     f"{limb}_scaleFactor.input2X",
                     force=True)
    
    # connect stretch factor to the condition's first term
    cmds.connectAttr(f"{limb}_scaleFactor.outputX",
                     f"{limb}_condition.firstTerm",
                     force=True)
    
    # connect stretch factor to color if true (stretch value)
    cmds.connectAttr(f"{limb}_scaleFactor.outputX",
                     f"{limb}_condition.colorIfTrueR",
                     force=True)
    
    # connect stretch value to ik joints (using translate instead of scale)
    for i in range(2):
        i = i + 1

        # create node to calculate translateY value
        cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{stretchJointList[i]}_translation")
        cmds.setAttr(f"{stretchJointList[i]}_translation.operation", 1)     # 1 = multiply

        # calculate translateY value with default translateY multiplied by scale factor
        cmds.connectAttr(f"{stretchJointList[i]}.translateY",
                         f"{stretchJointList[i]}_translation.input1X",
                         force=True)
        cmds.connectAttr(f"{limb}_condition.outColorR",
                         f"{stretchJointList[i]}_translation.input2X",
                         force=True)
        
        # connect translate output to ik and driver joints translateY
        cmds.connectAttr(f"{stretchJointList[i]}_translation.outputX",
                         f"{jointChain[i].replace("BIND", "IK")}.translateY",
                         force=True)
            
    
    # STRETCH CONTROL ATTRIBUTES

    # create stretchiness and stretch type attributes for main control
    cmds.select(IKFKswitch)
    cmds.addAttr(attributeType="float",
                    hasMaxValue=True, hasMinValue=True,
                    maxValue=1, minValue=0,
                    longName="stretchiness",
                    niceName="Stretchiness")
    cmds.setAttr(f"{IKFKswitch}.stretchiness", keyable=True)
    cmds.select(clear=True)

    
    cmds.select(IKFKswitch)
    cmds.addAttr(attributeType="enum",
                 enumName="Both:Stretch:Squash",
                 longName="stretchType",
                 niceName="Stretch Type")
    cmds.setAttr(f"{IKFKswitch}.stretchType", keyable=True)
    cmds.select(clear=True)


    # create blend colors node
    cmds.shadingNode("blendColors", asUtility=True, name=f"{limb}_blendColors")
    cmds.setAttr(f"{limb}_blendColors.color2",
                 1, 0, 0, type="double3")

    cmds.connectAttr(f"{limb}_scaleFactor.outputX",
                     f"{limb}_blendColors.color1R",
                     force=True)
    cmds.connectAttr(f"{limb}_blendColors.outputR",
                     f"{limb}_condition.colorIfTrueR",
                     force=True)

    # connect to foot control attribute
    cmds.connectAttr(f"{IKFKswitch}.stretchiness",
                     f"{limb}_blendColors.blender",
                     force=True)
    
    # connect attributes for stretch control
    # stretch type = both
    cmds.setAttr(f"{IKFKswitch}.stretchType", 0)
    cmds.setAttr(f"{limb}_condition.operation", 1) # 1 = not equal

    cmds.setDrivenKeyframe(f"{limb}_condition.operation",
                           currentDriver=f"{IKFKswitch}.stretchType")
    
    # stretch type = stretch
    cmds.setAttr(f"{IKFKswitch}.stretchType", 1)
    cmds.setAttr(f"{limb}_condition.operation", 3) # 3 = greater than

    cmds.setDrivenKeyframe(f"{limb}_condition.operation",
                           currentDriver=f"{IKFKswitch}.stretchType")
    
    # stretch type = squash
    cmds.setAttr(f"{IKFKswitch}.stretchType", 2)
    cmds.setAttr(f"{limb}_condition.operation", 5) # 5 = less than or equal

    cmds.setDrivenKeyframe(f"{limb}_condition.operation",
                           currentDriver=f"{IKFKswitch}.stretchType")
    
    # set default values
    cmds.setAttr(f"{IKFKswitch}.stretchiness", 1)
    cmds.setAttr(f"{IKFKswitch}.stretchType", 1)


    # fix hierarchy
    cmds.parent(stretchJointList[0], f"{limb}_IKFK")

    cmds.select(clear=True)

    return ["stretchiness", "stretchType"]



def createProxyAttributes(limb: str,
                          jointChain: list[str],
                          attributes: list[str]) -> str:
    """ Create proxy attributes and add them to relevant controls. """

    # get control names
    rootFKcontrol = jointChain[0].replace("BIND_JNT", "FK_CTRL")
    midFKcontrol = jointChain[1].replace("BIND_JNT", "FK_CTRL")
    endFKcontrol = jointChain[2].replace("BIND_JNT", "FK_CTRL")
    ikControl = f"{limb}_IK_CTRL"
    pvControl = f"{limb}_PV_CTRL"

    # get switch group name
    IKFKswitch = f"{limb}_IKFK_switch"

    # add proxy attributes to all controls in control list
    for control in [rootFKcontrol, midFKcontrol, endFKcontrol, ikControl, pvControl]:
        for attribute in attributes:
            cmds.select(control)
            cmds.addAttr(longName=attribute, proxy=f"{IKFKswitch}.{attribute}")
            cmds.setAttr(f"{control}.{attribute}", keyable=True)
            cmds.select(clear=True)



def createIKFKvisibility(limb: str,
                         jointChain: list[str]):
    """ Connect the visibility attribute of all the controls to the IK/FK switch. """

    # get control offset group names
    upperFKcontrol = jointChain[0].replace("BIND_JNT", "FK_GRP")
    midFKcontrol = jointChain[1].replace("BIND_JNT", "FK_GRP")
    lowerFKcontrol = jointChain[2].replace("BIND_JNT", "FK_GRP")
    ikControl = f"{limb}_IK_GRP"
    pvControl = f"{limb}_PV_GRP"

    # get switch group name
    IKFKswitch = f"{limb}_IKFK_switch"

    # create reverse node
    cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_IKFK_visibility_reverse")
    cmds.connectAttr(f"{IKFKswitch}.IKFKswitch", f"{limb}_IKFK_visibility_reverse.inputX")

    # connect visibility to relevant controls
    for control in [upperFKcontrol, midFKcontrol, lowerFKcontrol]:
        cmds.connectAttr(f"{IKFKswitch}.IKFKswitch", f"{control}.visibility")

    for control in [ikControl, pvControl]:
        cmds.connectAttr(f"{limb}_IKFK_visibility_reverse.outputX", f"{control}.visibility")



def _______________BUILD_______________(): pass


def buildLimbRig(limbTypeMenu: str,
                 globalScaleField: str,
                 stretchBox: str,
                 *args):
    """ Rig the limb. """

    # create list of joint hierarchy (including selected joint)
    rootJoint = cmds.ls(selection=True, type="joint")[0]
    midJoint = cmds.listRelatives(rootJoint, type="joint")[0]
    endJoint = cmds.listRelatives(midJoint, type="joint")[0]

    jointChain = [rootJoint, midJoint, endJoint]


    # BUILD NAMES FROM UI

    limbSide = rootJoint[0]
    limbType = cmds.optionMenu(limbTypeMenu, query=True, value=True).lower()
    globalScale = cmds.floatField(globalScaleField, query=True, value=True)
    stretch = cmds.checkBox(stretchBox, query=True, value=True)

    # create limb name
    limb = f"{limbSide}_{limbType}"


    # FIX HIERARCHY
    IKFKgroup = f"{limb}_IKFK"
    controlGroup = f"{limb}_controls"

    # create groups if they don't already exist
    if not cmds.objExists(IKFKgroup):
        cmds.group(name=IKFKgroup, empty=True)

        if cmds.objExists("RIG_DO_NOT_TOUCH"):
            cmds.parent(IKFKgroup, "RIG_DO_NOT_TOUCH")

    if not cmds.objExists(controlGroup):
        cmds.group(name=controlGroup, empty=True)


    # DRAWING OVERRIDES
    cmds.setAttr(f"{controlGroup}.overrideEnabled", True)
    cmds.setAttr(f"{controlGroup}.overrideRGBColors", True)

    if limbSide == "L":
        cmds.setAttr(f"{controlGroup}.overrideColorR", 1)
        cmds.setAttr(f"{controlGroup}.overrideColorG", 0)
        cmds.setAttr(f"{controlGroup}.overrideColorB", 0)
    else:
        cmds.setAttr(f"{controlGroup}.overrideColorR", 0)
        cmds.setAttr(f"{controlGroup}.overrideColorG", 0)
        cmds.setAttr(f"{controlGroup}.overrideColorB", 1)


    # BUILD RIG
    createFK(limb=limb,
             jointChain=jointChain,
             controlGroup=controlGroup,
             globalScale=globalScale,
             IKFKgroup=IKFKgroup)
    createIK(limb=limb,
             jointChain=jointChain,
             controlGroup=controlGroup,
             globalScale=globalScale,
             IKFKgroup=IKFKgroup)

    attributes = createIKFKswitch(limb=limb,
                                  jointChain=jointChain,
                                  IKFKgroup=IKFKgroup)

    if stretch:
        stretchAttributes = createStretch(limb=limb, jointChain=jointChain)
        attributes.append(stretchAttributes[0])
        attributes.append(stretchAttributes[1])

    createProxyAttributes(limb=limb, jointChain=jointChain, attributes=attributes)
    createIKFKvisibility(limb=limb, jointChain=jointChain)


createUI(buildLimbRig)