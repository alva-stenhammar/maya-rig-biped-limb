"""
RIG BIPED LIMB SCRIPT V.26.1
Created by Alva Stenhammar

Automatically rig limbs. Only works limbs with three joints (basically biped rigs).

TO ADD:
- add option to add fk clavicle control OR advanced ik clavicle setup
- add switch between advanced clavicle and fk clavicle

"""


import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import functools


# VARIABLES

globalScale = 1.0
controlSize = 1.0
limbStretch = True

rigHand = True
clavicleControl = True

rigFoot = True
reverseFoot = True

rootJoint = ""
limbSide = ""
limbType = ""
limb = ""

rigGroup = ""
controlGroup = ""
wsLocator = ""

IKFKswitch = ""
IKFKgroup = ""
limbControlGroup = ""
handControlGroup = ""
footControlGroup = ""

FKcontrols = []
IKcontrols = []



def _______________UI_______________(): pass


def toggleFootOptions(footBox: str,
                      revFootBox: str,
                      *args):
    """ Toggle the options for the foot rig when the rig foot checkbox is toggled. """

    if cmds.checkBox(footBox, query=True, value=True) == True:
        cmds.checkBox(revFootBox, edit=True, enable=True)
        cmds.checkBox(revFootBox, edit=True, value=True)
    else:
        cmds.checkBox(revFootBox, edit=True, enable=False)
        cmds.checkBox(revFootBox, edit=True, value=False)



def createLineSeparator(parent: str) -> str:
    """ Create custom line separator.
    
    Return separator. """

    return cmds.separator(height=2,
                          style="none",
                          backgroundColor=(0.2, 0.2, 0.2),
                          parent=parent)



def createBlankSeparator(parent: str) -> str:
    """ Create custom blank separator.
    
    Return separator. """

    return cmds.separator(height=5,
                          style="none",
                          parent=parent)



def createColumnLayout(parent: str) -> str:
    """ Create row/column layout with custom settings.

    Return layout. """

    return cmds.rowColumnLayout(numberOfColumns=2,
                                columnWidth=[(1, 130), (2, 130)],
                                columnOffset=[(1, "right", 10), (2, "left", 10)],
                                rowSpacing=(1, 5),
                                parent=parent)



def createFrameLayout(label: str, parent: str) -> str:
    """ Create frame layout layout with custom settings.

    Return layout. """

    return cmds.frameLayout(label=label,
                            width=300,
                            marginWidth=20,
                            marginHeight=10,
                            backgroundShade=True,
                            font="boldLabelFont",
                            parent=parent)



def createButton(label: str, parent: str) -> str:
    """ Create button with custom settings.
    
    Return button. """

    cmds.rowLayout(numberOfColumns=1,
                   columnWidth=(1, 260),
                   parent=parent)
    
    return cmds.button(label=label, width=260)



def createUI(buildArmRig, buildLegRig):
    """ Create and open the UI. """

    # WINDOW CREATION
    windowID = "rigBipedLimbWindowID"
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
    cmds.window(windowID, title="Rig Biped Limb", sizeable=True)


    # LAYOUTS
    mainLayout = cmds.columnLayout(width=310, margins=5)

    cmds.columnLayout(margins=10, parent=mainLayout)
    cmds.text(label="Rig Biped Limb Tool",
              width=280,
              font="boldLabelFont")
    cmds.separator(height=10, style="none")


    # LAYOUT SETUP
    layout1 = createFrameLayout("Global Settings", mainLayout)
    createBlankSeparator(parent=mainLayout)

    
    layout2 = createFrameLayout("Arm Rig", mainLayout)
    cmds.text(label="Select shoulder joint to rig.",
                width=260, height=10,
                font="smallPlainLabelFont")
    createLineSeparator(layout2)
    createBlankSeparator(parent=mainLayout)


    layout3 = createFrameLayout("Leg Rig", mainLayout)
    cmds.text(label="Select hip joint to rig.",
                width=260, height=10,
                font="smallPlainLabelFont")
    createLineSeparator(layout3)
    createBlankSeparator(parent=mainLayout)


    # LAYOUT-1: GLOBAL SETTINGS

    createColumnLayout(parent=layout1)

    cmds.text(label="Global scale:")
    globalScaleField = cmds.floatField(value=1, precision=2, width=50)

    cmds.text(label="Control size:")
    controlSizeField = cmds.floatField(value=1, precision=2, width=50)

    cmds.text(label="Stretchy limb:")
    limbStretchBox = cmds.checkBox(label="", value=True)


    # LAYOUT-2: ARM
    
    createColumnLayout(parent=layout2)

    # options
    cmds.text(label="Rig hand:")
    handBox = cmds.checkBox(label="", value=True)

    cmds.text(label="Add clavicle control:")
    clavicleBox = cmds.checkBox(label="", value=True)

    # apply button
    cmds.separator(height=1, style="none", enableBackground=False, parent=layout2)
    armApplyButton = createButton("Rig Arm", layout2)


    # LAYOUT-3: LEG
    
    createColumnLayout(parent=layout3)

    # options
    cmds.text(label="Rig foot:")
    footBox = cmds.checkBox(label="", value=True)

    cmds.text(label="Reverse foot:")
    revFootBox = cmds.checkBox(label="", value=True)

    # apply button
    cmds.separator(height=1, style="none", enableBackground=False, parent=layout3)
    legApplyButton = createButton("Rig Leg", layout3)


    # CREDITS TEXT
    cmds.columnLayout(margins=10, parent=mainLayout)
    createBlankSeparator(parent=mainLayout)
    
    cmds.text(label="Created by Alva Stenhammar",
              width=280,
              font="obliqueLabelFont")

    
    # ADD COMMANDS

    # rig foot box
    cmds.checkBox(footBox, edit=True,
                  changeCommand=functools.partial(toggleFootOptions,
                                                  footBox,
                                                  revFootBox))


    # apply buttons
    cmds.button(armApplyButton, edit=True,
                command=functools.partial(buildArmRig,
                                          globalScaleField,
                                          controlSizeField,
                                          limbStretchBox,
                                          handBox,
                                          clavicleBox))

    cmds.button(legApplyButton, edit=True,
                command=functools.partial(buildLegRig,
                                          globalScaleField,
                                          controlSizeField,
                                          limbStretchBox,
                                          footBox,
                                          revFootBox))

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



def calculatePVposition(jointChain: list[str]) -> list[float]:
    """ Calculate pole vector position based on joint chain.
    
    Return position as [x, y, z]. """

    startPos = cmds.xform(jointChain[0], query=True, worldSpace=True, translation=True)
    midPos = cmds.xform(jointChain[1], query=True, worldSpace=True, translation=True)
    endPos = cmds.xform(jointChain[2], query=True, worldSpace=True, translation=True)

    startVec = om.MVector(startPos[0], startPos[1], startPos[2])
    midVec = om.MVector(midPos[0], midPos[1], midPos[2])
    endVec = om.MVector(endPos[0], endPos[1], endPos[2])

    startEnd = endVec - startVec
    startMid = midVec - startVec

    dot = startMid * startEnd
    proj = float(dot) / float(startEnd.length())
    projVec = startEnd.normal() * proj
    arrowVec = (startMid - projVec) * 5 * globalScale
    finalVec = arrowVec + midVec

    return [finalVec.x, finalVec.y, finalVec.z]



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



def setDrawingOverrides(object: str, colour: str = ""):
    """ Set drawing overrides for a specific object.
    
    Colours:
    - blank = based on position
    - pink """

    cmds.setAttr(f"{object}.overrideEnabled", True)

    if colour == "":
        cmds.setAttr(f"{object}.overrideRGBColors", True)

        if limbSide == "L":
            cmds.setAttr(f"{object}.overrideColorR", 1)
            cmds.setAttr(f"{object}.overrideColorG", 0.15)
            cmds.setAttr(f"{object}.overrideColorB", 0)
        else:
            cmds.setAttr(f"{object}.overrideColorR", 0.1)
            cmds.setAttr(f"{object}.overrideColorG", 0.4)
            cmds.setAttr(f"{object}.overrideColorB", 1)

    elif colour == "pink":
        cmds.setAttr(f"{object}.overrideRGBColors", False)
        cmds.setAttr(f"{object}.overrideColor", 31)

    elif colour == "purple":
        cmds.setAttr(f"{object}.overrideRGBColors", False)
        cmds.setAttr(f"{object}.overrideColor", 30)

    elif colour == "yellow":
        cmds.setAttr(f"{object}.overrideRGBColors", True)
        cmds.setAttr(f"{object}.overrideColorR", 1)
        cmds.setAttr(f"{object}.overrideColorG", 1)
        cmds.setAttr(f"{object}.overrideColorB", 0.4)



def getFingers() -> list[list[str]]:
    """ Create lists of the finger joints. """

    fingerList = []
    fingers = cmds.listRelatives(rootJoint, children=True, type="joint")

    while len(fingers) != 5:
        fingers = cmds.listRelatives(fingers, children=True, type="joint")

        if fingers == None:
            break

    for finger in fingers:
        fingerJoints = cmds.listRelatives(finger, allDescendents=True, type="joint")
        fingerJoints.append(finger)
        fingerJoints.reverse()

        fingerList.append(fingerJoints)

    return fingerList



def getToes() -> list[list[str]]:
    """ Create lists of the toe joints. """

    toeList = []
    toes = cmds.listRelatives(rootJoint, children=True, type="joint")

    while len(toes) != 5:
        toes = cmds.listRelatives(toes, children=True, type="joint")

        if toes == None:
            break

    for toe in toes:
        toeJoints = cmds.listRelatives(toe, allDescendents=True, type="joint")
        toeJoints.append(toe)
        toeJoints.reverse()

        toeList.append(toeJoints)

    return toeList



def _______________CREATE_______________(): pass


def createHierarchy():
    """ Create hierarchy with groups. """

    global rigGroup
    global controlGroup
    global IKFKgroup
    global limbControlGroup
    global handControlGroup
    global footControlGroup
    global wsLocator

    rigGroup = "RIG_DO_NOT_TOUCH"
    controlGroup = "controls"
    wsLocator = "worldSpace_LOC"

    IKFKgroup = f"{limb}_IKFK"
    limbControlGroup = f"{limb}_controls"
    handControlGroup = f"{limbSide}_hand_controls"
    footControlGroup = f"{limbSide}_foot_controls"
    

    # create groups if they don't already exist and parent them correctly
    if not cmds.objExists(rigGroup):
        cmds.group(name=rigGroup, empty=True)

    if not cmds.objExists(controlGroup):
        cmds.group(name=controlGroup, empty=True)

    if not cmds.objExists(IKFKgroup):
        cmds.group(name=IKFKgroup, empty=True)
        cmds.parent(IKFKgroup, rigGroup)

    if not cmds.objExists(limbControlGroup):
        cmds.group(name=limbControlGroup, empty=True)
        cmds.parent(limbControlGroup, controlGroup)

    if not cmds.objExists(wsLocator):
        cmds.spaceLocator(name=wsLocator)
        cmds.parent(wsLocator, rigGroup)

    if limbType == "arm" and rigHand:
        if not cmds.objExists(handControlGroup):
            cmds.group(name=handControlGroup, empty=True)
            cmds.parent(handControlGroup, controlGroup)

    if limbType == "leg" and rigFoot:
        if not cmds.objExists(footControlGroup):
            cmds.group(name=footControlGroup, empty=True)
            cmds.parent(footControlGroup, controlGroup)



def createControl(name: str,
                  shape: str,
                  size: float) -> tuple[str]:
    """ Create a control with different shapes.

    Return name of control and offset group.

    Control shapes:
    - circle
    - locator
    - pyramid
    - box
    - arrows
    - plus
    - star
    - handle """

    global FKcontrols
    global IKcontrols
    global footFKcontrols
    global footIKcontrols

    if shape == "circle":
        control = cmds.circle(name=name, normal=(0, 1, 0))[0]


    elif shape == "locator":
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


    elif shape == "curvedBox":
        pass


    elif shape == "4arrows":
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

    
    elif shape == "star":
        control = cmds.circle(name=name, sections=16)[0]
        
        count = 0

        for i in range(16):
            if count % 2 == 0:
                cmds.select(f"{control}.cv[{str(i)}]", add=True)
            count += 1
        
        cmds.scale(0.7, 0.7, 0.7)
        cmds.select(clear=True)


    elif shape == "handle":

        # circle handle
        # handleTransform = cmds.circle(normal=(1, 0, 0),
        #                               center=(0, s + l, 0),
        #                               radius=s)[0]

        # square handle
        handleTransform = cmds.curve(degree=1,
                                     point=[(1, 0, 1), (-1, 0, 1), (-1, 0, -1), (1, 0, -1), (1, 0, 1)])
        cmds.move(10, 0, 0, handleTransform)
        cmds.makeIdentity(handleTransform, apply=True,
                          translate=True, rotate=True, scale=True)
    
        curve = cmds.curve(degree=1, point=[(0, 0, 0), (9, 0, 0)])
        handleShape = cmds.listRelatives(handleTransform, shapes=True)
    
        # make handle and curve into one transform object
        cmds.parent(handleShape[0], curve, relative=True, shape=True)
        cmds.delete(handleTransform)

        control = cmds.rename(curve, name)

        # fix rotation
        cmds.rotate(0, 90, 0, control)
        cmds.makeIdentity(control, apply=True, rotate=True)


    elif shape == "arrow":
        positions = [(-0.5, 0, 1), (-0.5, 0, 0),
                     (-1, 0, 0), (0, 0, -1),
                     (1, 0, 0), (0.5, 0, 0),
                     (0.5, 0, 1), (-0.5, 0, 1)]

        control = cmds.curve(name=name, degree=1, point=positions)


    # scale to size & fix rotation, freeze transforms and delete history
    cmds.scale(size, size, size, control, relative=True, objectSpace=True)
    cmds.rotate(0, 0, 90, control)
    cmds.makeIdentity(control, apply=True, scale=True, rotate=True)
    cmds.delete(control, constructionHistory=True)

    # add offset group
    group = cmds.group(empty=True, name=control.replace("CTRL", "GRP"))
    cmds.parent(control, group)

    # add to FK or IK control group
    if control.find("FK") != -1:
        FKcontrols.append(control)

    if control.find("IK") != -1 or control.find("PV") != -1:
        IKcontrols.append(control)

    cmds.select(clear=True)

    return (control, group)



def createProxyAttributes(attributes: list[str]) -> str:
    """ Create proxy attributes and add them to relevant controls. """

    # add proxy attributes to all controls in control list
    for control in FKcontrols + IKcontrols:
        for attribute in attributes:
            cmds.select(control)
            cmds.addAttr(longName=attribute, proxy=f"{IKFKswitch}.{attribute}")
            cmds.setAttr(f"{control}.{attribute}", keyable=True)
            cmds.select(clear=True)
    



def createIKFKvisibility():
    """ Connect the visibility attribute of all the controls to the IK/FK switch. """
    global FKcontrols
    global IKcontrols

    # create reverse node
    reverse = cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_IKFK_visibility_reverse")
    cmds.connectAttr(f"{IKFKswitch}.IKFKswitch", f"{reverse}.inputX")

    if limbType == "leg" and reverseFoot:
        footReverse = cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_foot_IKFK_visibility_reverse")
        cmds.connectAttr(f"{IKFKswitch}.footIKFKswitch", f"{footReverse}.inputX")

    # connect visibility to relevant control offset groups
    for control in FKcontrols:
        if limbType == "leg" and reverseFoot and control.find("Toe") != -1:
            cmds.connectAttr(f"{IKFKswitch}.footIKFKswitch", f"{control.replace("CTRL", "GRP")}.visibility")
        else:
            cmds.connectAttr(f"{IKFKswitch}.IKFKswitch", f"{control.replace("CTRL", "GRP")}.visibility")

    for control in IKcontrols:
        if limbType == "leg" and reverseFoot and control.find("toe") != -1:
            cmds.connectAttr(f"{footReverse}.outputX", f"{control.replace("CTRL", "GRP")}.visibility")
        else:
            cmds.connectAttr(f"{reverse}.outputX", f"{control.replace("CTRL", "GRP")}.visibility")

    # clear controls lists to prevent error when undoing and redoing script
    FKcontrols.clear()
    IKcontrols.clear()
    



def _______________CREATE_LIMB_______________(): pass


def createLimbFK(jointChain: list[str]):
    """ Create FK setup for a limb.  """

    # create fk joint chain
    for bindJoint in jointChain:
        newJoint = bindJoint.replace("BIND", "FK")

        cmds.joint(name=newJoint, radius=1)
        cmds.matchTransform(newJoint, bindJoint)
        cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

    cmds.select(clear=True)

    controls = []

    for i, bindJoint in enumerate(jointChain):
        controlName = bindJoint.replace("BIND_JNT", "FK_CTRL")
        control, group = createControl(name=controlName, shape="circle", size=(7 * controlSize))

        # move to bind joint and transfer transforms
        cmds.matchTransform(group, bindJoint)
        transferTransformsToOPM(group)

        # fix rotation
        cmds.setAttr(f"{control}.rotateX", 180)

        if limbType == "leg" and i == 2:
            cmds.setAttr(f"{control}.rotateZ", 90)
            
        cmds.makeIdentity(control, apply=True, rotate=True)

        # parent bind joint to control
        cmds.parentConstraint(control, bindJoint.replace("BIND", "FK"), maintainOffset=True)

        controls.append(control)

        # parent to previous control
        if i != 0:
            cmds.parent(group, controls[i-1])


    # add clavicle control
    # if limbType == "arm" and clavicleControl:
    #     clavicleJoint = cmds.pickWalk(jointChain[0], direction='up')[0]
    #     clavicleJoint = cmds.pickWalk(clavicleJoint, direction='up')[0]

    #     control, group = createControl(name=clavicleJoint.replace("BIND_JNT", "FK_CTRL"), shape="circle", size=(5 * controlSize))
    #     cmds.matchTransform(group, clavicleJoint)
    #     transferTransformsToOPM(group)

    #     cmds.parent(controls[0], control)


    # add ankle locator at fk joint position and parent to fk ankle ctrl to help with matching ik to fk
    if limbType == "leg":
        ankleLocator = cmds.spaceLocator(name=jointChain[2].replace("BIND_JNT", "LOC"))[0]
        cmds.matchTransform(ankleLocator, jointChain[2], position=True, rotation=False)
        cmds.parent(ankleLocator, jointChain[2].replace("BIND_JNT", "FK_CTRL"))
        cmds.setAttr(f"{ankleLocator}.visibility", 0)


    # HIERARCHY
    # if limbType == "arm" and clavicleControl:
    #     cmds.parent(group, limbControlGroup)
    # else:
    cmds.parent(controls[0].replace("CTRL", "GRP"), limbControlGroup)

    cmds.parent(jointChain[0].replace("BIND", "FK"), IKFKgroup)
        
    cmds.select(clear=True)



def createLimbIK(jointChain: list[str]):
    """ Create the IK setup for a limb. """

    global IKcontrols

    IKrootControl = jointChain[0].replace("BIND_JNT", "IK_CTRL")
    IKrootGroup = IKrootControl.replace("CTRL", "GRP")
    IKcontrol = f"{limb}_IK_CTRL"
    IKgroup = IKcontrol.replace("CTRL", "GRP")
    PVcontrol = f"{limb}_PV_CTRL"
    PVgroup = PVcontrol.replace("CTRL", "GRP")
    IKjoints = []

    # create joints
    for bindJoint in jointChain:
        newJoint = bindJoint.replace("BIND", "IK")
        IKjoints.append(newJoint)

        cmds.joint(name=newJoint, radius=1)
        cmds.matchTransform(newJoint, bindJoint)
        cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

    cmds.select(clear=True)

    # set preferred angle
    for joint in IKjoints:
        currentRotation = cmds.xform(joint, query=True, rotation=True, worldSpace=False)
        for i, axis in enumerate(["X", "Y", "Z"]):
            cmds.setAttr(f'{joint}.preferredAngle{axis}', currentRotation[i])


    # CREATE CONTROLS

    # limb control (arm/leg)
    if not cmds.objExists(IKcontrol):
        IKcontrol, IKgroup = createControl(name=IKcontrol, shape="box", size=(5 * controlSize))
        cmds.matchTransform(IKgroup, jointChain[2])

        if limbType == "leg":
            for axis in ["X", "Y", "Z"]:
                cmds.setAttr(f"{IKgroup}.rotate{axis}", 0)

        transferTransformsToOPM(IKgroup)
    else:
        IKcontrols.append(IKcontrol)

    # root control (shoulder/hip)
    if not cmds.objExists(IKrootControl):
        IKrootControl, IKrootGroup = createControl(name=IKrootControl, shape="handle", size=(1 * controlSize))

        if limbSide == "R":
            cmds.rotate(0, 180, 0, IKrootControl)
            cmds.makeIdentity(IKrootControl, apply=True, rotate=True)

        cmds.matchTransform(IKrootGroup, jointChain[0])
        transferTransformsToOPM(IKgroup)
    else:
        IKcontrols.append(IKrootControl)

    # pole vector
    if not cmds.objExists(PVcontrol):
        PVcontrol, PVgroup = createControl(name=PVcontrol, shape="pyramid", size=(1 * controlSize))

        cmds.setAttr(f"{PVcontrol}.rotateX", -90)
        cmds.makeIdentity(PVcontrol, apply=True)

        # move PV to correct location
        PVpos = calculatePVposition(jointChain)
        cmds.move(PVpos[0], PVpos[1], PVpos[2], PVgroup)

        # move translate values to offset parent matrix
        transferTransformsToOPM(PVgroup)
    else:
        IKcontrols.append(PVcontrol)


    # IK HANDLE
    # create IK handle and parent to correct control
    cmds.ikHandle(name=f"{limb}_HNDL",
                  solver="ikRPsolver",
                  startJoint=jointChain[0].replace("BIND", "IK"),
                  endEffector=jointChain[2].replace("BIND", "IK"))
    cmds.parent(f"{limb}_HNDL", IKcontrol)

    # hide IK handle
    cmds.setAttr(f"{limb}_HNDL.visibility", 0)

    # add orient constraint for wrist control
    if limbType == "arm":
        cmds.orientConstraint(IKcontrol, jointChain[2].replace("BIND", "IK"))

    # add PV constraint
    cmds.poleVectorConstraint(PVcontrol, f"{limb}_HNDL")


    # POLE VECTOR OFFSET

    # create follow attribute
    cmds.select(PVcontrol)
    cmds.addAttr(attributeType="float",
                    hasMaxValue=True, hasMinValue=True,
                    maxValue=1, minValue=0,
                    longName="follow",
                    niceName="Follow")
    cmds.setAttr(f"{PVcontrol}.follow", keyable=True)
    cmds.setAttr(f"{PVcontrol}.follow", 1)
    cmds.select(clear=True)
    
    # pole vector offset setup
    offsetParent = cmds.spaceLocator(name=f"{limb}_PV_offsetParent")[0]
    upObject = cmds.spaceLocator(name=f"{limb}_PV_upObject")[0]

    cmds.matchTransform(upObject, jointChain[0].replace("BIND", "IK"), position=True, rotation=False)

    cmds.move(0, 0, (50 * globalScale), upObject,
              relative=True, objectSpace=True, worldSpaceDistance=True)

    cmds.pointConstraint(jointChain[0].replace("BIND", "IK"), offsetParent)
    cmds.aimConstraint(IKcontrol, offsetParent,
                       aim=(1, 0, 0), upVector=(0, 1, 0),
                       maintainOffset=True,
                       worldUpType="object",
                       worldUpObject=upObject)
    
    PVconstraint = cmds.parentConstraint(wsLocator, offsetParent, PVgroup, maintainOffset=True)[0]
    reverseNode = cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_PV_follow_REV_JNTerse")

    cmds.connectAttr(f"{PVcontrol}.follow", f"{reverseNode}.inputX")
    cmds.connectAttr(f"{reverseNode}.outputX", f"{PVconstraint}.{wsLocator}W0")
    cmds.connectAttr(f"{PVcontrol}.follow", f"{PVconstraint}.{offsetParent}W1")

    # aim constraint to knee/elbow joint
    cmds.aimConstraint(jointChain[1], PVcontrol)


    # add PV annotation arrow
    PVarrow = f"{limb}_PV_ARROW"
    annotationShape = cmds.createNode("annotationShape", name=f"{PVarrow}Shape")

    cmds.connectAttr(f"{limb}_PV_CTRLShape.worldMatrix[0]",
                        f"{annotationShape}.dagObjectMatrix[0]")

    cmds.matchTransform(PVarrow, f"{jointChain[1].replace("BIND", "IK")}")
    cmds.parentConstraint(f"{jointChain[1].replace("BIND", "IK")}", PVarrow, maintainOffset=True)
    cmds.parent(PVarrow, PVgroup)
    IKcontrols.append(PVarrow)


    # add pv locator at pv position and parent to fk elbow ctrl to help with matching ik to fk
    pvLocator = cmds.spaceLocator(name=jointChain[1].replace("BIND_JNT", "PV_LOC"))[0]
    cmds.matchTransform(pvLocator, PVcontrol)
    cmds.parent(pvLocator, jointChain[1].replace("BIND_JNT", "FK_CTRL"))
    cmds.setAttr(f"{pvLocator}.visibility", 0)


    # parent constrain ikfk group to shoulder/hip control
    cmds.parentConstraint(IKrootControl, IKFKgroup)

    # constrain root ik control to chest or cog control if they exist
    if limbType == "arm" and cmds.objExists("C_chest_CTRL"):
        cmds.parentConstraint("C_chest_CTRL", IKrootGroup, maintainOffset=True)

    if limbType == "leg" and cmds.objExists("C_cog_CTRL"):
        cmds.parentConstraint("C_cog_CTRL", IKrootGroup, maintainOffset=True)

    
    # HIERARCHY
    cmds.parent(IKjoints[0], IKFKgroup)

    cmds.parent(IKgroup, limbControlGroup)
    cmds.parent(PVgroup, limbControlGroup)
    cmds.parent(IKrootGroup, limbControlGroup)
    
    cmds.parent(offsetParent, f"{limb}_IKFK")
    cmds.parent(upObject, f"{limb}_IKFK")

    cmds.select(clear=True)



def createLimbIKFKswitch(jointChain: list[str], toeList: list[str] = []) -> list[str]:
    """ Create the switch between FK and IK joints, then connect it to the IK/FK switch attribute.
    
    Return list of created attributes. """

    global IKFKswitch

    IKFKswitch = f"{limb}_IKFK_switch"

    # ATTRIBUTES
    # create switch group
    cmds.group(empty=True, name=IKFKswitch)
    cmds.parent(IKFKswitch, IKFKgroup)
        
    # add attribute divider to switch group
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
    reverse = cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_IKFK_reverse")
    cmds.connectAttr(f"{IKFKswitch}.IKFKswitch",
                     f"{reverse}.inputX",
                     force=True)

    # set up switch for limb
    for i, bindJoint in enumerate(jointChain):
        # create FK and IK joint names
        FKjoint = bindJoint.replace("BIND", "FK")
        IKjoint = bindJoint.replace("BIND", "IK")

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
    """ Add stretch to IK limb with options for stretchiness and stretch type.
    
    Return list of created attributes. """

    IKcontrol = f"{limb}_IK_CTRL"
    stretchJointList = []

    # create stretch joints
    for bindJoint in jointChain:
        newJoint = bindJoint.replace("BIND", "STRETCH")

        cmds.joint(name=newJoint, radius=1)
        cmds.matchTransform(newJoint, bindJoint)
        cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

        stretchJointList.append(newJoint)

    cmds.select(clear=True)

    # parent constrain stretch root joint to chest/cog control if they exist
    if limbType == "arm" and cmds.objExists("C_chest_CTRL"):
        cmds.parentConstraint("C_chest_CTRL", stretchJointList[0], maintainOffset=True)

    if limbType == "leg" and cmds.objExists("C_cog_CTRL"):
        cmds.parentConstraint("C_cog_CTRL", stretchJointList[0], maintainOffset=True)


    # create end position locator, move to end joint, and parent to end joint control
    cmds.spaceLocator(name=f"{limb}_endPos_LOC")
    cmds.matchTransform(f"{limb}_endPos_LOC", jointChain[2])
    cmds.parent(f"{limb}_endPos_LOC", IKcontrol)

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

        # create node to calculate translateX value
        cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{stretchJointList[i]}_translation")
        cmds.setAttr(f"{stretchJointList[i]}_translation.operation", 1)     # 1 = multiply

        # calculate translateX value with default translateX multiplied by scale factor
        cmds.connectAttr(f"{stretchJointList[i]}.translateX",
                         f"{stretchJointList[i]}_translation.input1X",
                         force=True)
        cmds.connectAttr(f"{limb}_condition.outColorR",
                         f"{stretchJointList[i]}_translation.input2X",
                         force=True)
        
        # connect translate output to ik and driver joints translateX
        cmds.connectAttr(f"{stretchJointList[i]}_translation.outputX",
                         f"{jointChain[i].replace("BIND", "IK")}.translateX",
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



def createClavicle(jointChain: list[str]):
    """ Create advanced clavicle setup. Taken from mrpaulpopov's maya-clavicle-rig-tool on GitHub. """

    # names
    shoulderGuide = f"{limbSide}_shoulder_BIND_JNT"
    armIntersection = "C_chest_BIND_JNT"
    scapula1Guide = f"{limbSide}_scapula1_GUIDE"
    clavicle1Joint = f"{limbSide}_clavicle1_BIND_JNT"
    scapula2Guide = f"{limbSide}_scapula2_GUIDE"
    trap1Guide = f"{limbSide}_trap1_GUIDE"
    trap2Guide = f"{limbSide}_trap2_GUIDE"
    pecGuide = f"{limbSide}_pec_GUIDE"
    latGuide = f"{limbSide}_lat_GUIDE"
    shrinkIntensity = 0.1

    primaryAxis = "X"
    secondaryAxis = "Z"

    if secondaryAxis == 'X':
        secondaryAxisR = 'rx'
    elif secondaryAxis == 'Y':
        secondaryAxisR = 'ry'
    elif secondaryAxis == 'Z':
        secondaryAxisR = 'rz'

    upstreamingJoint = cmds.pickWalk(armIntersection, direction='down')[0]
    clavicle2Joint = cmds.pickWalk(clavicle1Joint, direction='down')[0]


    # JOINTS

    # create new joint chains
    scapulaRotEndJoint = f"{limbSide}_scapulaBase_DRIVER_JNT"
    scapula1Joint = scapula1Guide.replace("GUIDE", "BIND_JNT")
    scapula2Joint = scapula2Guide.replace("GUIDE", "BIND_JNT")
    trap1Joint = trap1Guide.replace("GUIDE", "BIND_JNT")
    trap2Joint = trap2Guide.replace("GUIDE", "BIND_JNT")
    pecJoint = pecGuide.replace("GUIDE", "BIND_JNT")
    latJoint = latGuide.replace("GUIDE", "BIND_JNT")

    cmds.select(clear=True)
    
    # scapula joint chain
    cmds.joint(name=scapulaRotEndJoint, radius=1)
    cmds.joint(name=scapula1Joint, radius=1)
    cmds.joint(name=scapula2Joint, radius=1)

    cmds.select(clear=True)

    # trap joint chain
    cmds.joint(name=trap1Joint, radius=1)
    cmds.joint(name=trap2Joint, radius=1)
    cmds.select(clear=True)

    # pec joint
    cmds.joint(name=pecJoint, radius=1)
    cmds.select(clear=True)

    # lat joint
    cmds.joint(name=latJoint, radius=1)
    cmds.select(clear=True)

    # match transforms
    cmds.matchTransform(scapulaRotEndJoint, shoulderGuide)

    for joint in [scapula1Joint, scapula2Joint, trap1Joint, trap2Joint, pecJoint, latJoint]:
        cmds.matchTransform(joint, joint.replace("BIND_JNT", "GUIDE"))
        cmds.makeIdentity(joint, apply=True, rotate=True)

    # clean and joint orient
    cmds.makeIdentity(scapulaRotEndJoint, apply=True, rotate=True)
    cmds.select(scapulaRotEndJoint)
    cmds.joint(e=True,  oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
    cmds.select(trap1Joint)
    cmds.joint(e=True,  oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)

    cmds.select(scapula2Joint)
    mel.eval("joint -e  -oj none -ch -zso;")
    cmds.select(trap2Joint)
    mel.eval("joint -e  -oj none -ch -zso;")


    # HIERARCHY

    # create groups
    skeletonGroup = "skeleton"
    pecGroup = cmds.group(empty=True, name=pecJoint.replace("BIND_JNT", "GRP"))
    latGroup = cmds.group(empty=True, name=latJoint.replace("BIND_JNT", "GRP"))

    # parent
    cmds.parent(scapulaRotEndJoint, jointChain[0])
    cmds.parent(trap1Joint, clavicle2Joint)
    cmds.parent(pecJoint, pecGroup)
    cmds.parent(latJoint, latGroup)
    cmds.parent(pecGroup, skeletonGroup)
    cmds.parent(latGroup, skeletonGroup)

    # constraints
    cmds.parentConstraint(armIntersection, pecGroup, maintainOffset=True)
    cmds.pointConstraint(clavicle2Joint, armIntersection, pecJoint,
                         weight=0.5, skip="x", maintainOffset=True)
    cmds.pointConstraint(clavicle2Joint, armIntersection, latJoint,
                         weight=0.5, skip='y', sk='z', maintainOffset=True)


    # CONTROL

    IKhandle = cmds.ikHandle(startJoint=clavicle1Joint, endEffector=clavicle2Joint,
                             name=f"{limbSide}_clavicle_HNDL", solver='ikSCsolver')[0]
    control, group = createControl(name=f"{limbSide}_clavicle_CTRL", shape="arrow", size=(2 * controlSize))

    if limbSide == "L":
        rot = -45
        offset = 7
    else:
        rot = 45
        offset = -7

    # move into position
    cmds.rotate(-90, 90, rot, control)
    cmds.select(f"{control}.cv[*]")
    cmds.move(offset, 7, 0, relative=True)
    cmds.select(clear=True)
    cmds.makeIdentity(control, apply=True, translate=True, rotate=True, scale=True)

    pc = cmds.pointConstraint(IKhandle, group, maintainOffset=False)
    cmds.delete(pc)
    cmds.parentConstraint(control, IKhandle, maintainOffset=True)

    transferTransformsToOPM(group)


    # AIM CONSTRAINTS

    locator = "C_shoulderUp_LOC"

    if not cmds.objExists(locator):
        cmds.spaceLocator(name=locator)
        cmds.setAttr(f"{locator}.visibility", 0)

    if not isParentOf(armIntersection, locator):
        cmds.parent(locator, armIntersection)

    worldUp = [0, 0, 0]

    if primaryAxis == 'X':
        worldUp[0] = 1
    elif primaryAxis == 'Y':
        worldUp[1] = 1
    elif primaryAxis == 'Z':
        worldUp[2] = 1

    for i, joint in enumerate([trap1Joint, scapulaRotEndJoint, scapula1Joint]):
        if i < 2:
            aimObject = upstreamingJoint
        else:
            aimObject = armIntersection

        cmds.aimConstraint(aimObject, joint, maintainOffset=True,
                            worldUpType="objectrotation", worldUpObject=locator,
                            worldUpVector=(worldUp[0], worldUp[1], worldUp[2]))

    # SCAPULA TWEAK

    # nodes
    multi = cmds.createNode("multiplyDivide", name=f"{limbSide}_scapula_multi")
    pma = cmds.createNode("plusMinusAverage", name=f"{limbSide}_scapula_pma")
    condition1 = cmds.createNode("condition", name=f"{limbSide}_scapula_condition1")
    condition2 = cmds.createNode("condition", name=f"{limbSide}_scapula_condition2")

    # set attr
    offset = cmds.getAttr(f"{scapula1Joint}.translate{primaryAxis}")

    cmds.setAttr(f"{multi}.input1X", float(shrinkIntensity))  # multiplier
    cmds.setAttr(f"{pma}.input1D[0]", offset)  # offset
    cmds.setAttr(f"{condition1}.operation", 4)   # 4 = less than
    cmds.setAttr(f"{condition1}.colorIfFalseR", offset)
    cmds.setAttr(f"{condition2}.operation", 2)   # 2 = greater than
    cmds.setAttr(f"{condition2}.secondTerm", 0)
    cmds.setAttr(f"{condition2}.colorIfFalseR", 0)

    # connect attr
    cmds.connectAttr(f"{clavicle1Joint}.{secondaryAxisR}", f"{multi}.input2X")
    cmds.connectAttr(f"{multi}.ox", f"{pma}.input1D[1]")
    cmds.connectAttr(f"{pma}.o1", f"{condition1}.colorIfTrueR")
    cmds.connectAttr(f"{clavicle1Joint}.{secondaryAxisR}", f"{condition1}.firstTerm")
    cmds.connectAttr(f"{condition1}.ocr", f"{condition2}.firstTerm")
    cmds.connectAttr(f"{condition1}.ocr", f"{condition2}.colorIfTrueR")
    cmds.connectAttr(f"{condition2}.ocr", f"{scapula1Joint}.translate{primaryAxis}")

    # delete guides
    for guide in [scapula1Guide, scapula2Guide, trap1Guide, trap2Guide, pecGuide, latGuide]:
        cmds.delete(guide)


    # HIERARCHY & PARENTING
    cmds.parent(group, limbControlGroup)
    cmds.parent(IKhandle, IKFKgroup)
    cmds.parentConstraint(control, jointChain[0].replace("BIND_JNT", "FK_GRP"), maintainOffset=True)
    cmds.parentConstraint(control, jointChain[0].replace("BIND_JNT", "IK_GRP"), maintainOffset=True)


def ___________CREATE_EXTREMITY___________(): pass


def createExtremityFK(jointList: list[list[str]], jointChain: list[str]):
    """ Create the FK setup for a hand or foot. """

    # foot with ik and fk setup
    if limbType == "leg" and reverseFoot:
        for toe in jointList:
            for joint in toe:
                # create new joint chain if it's a foot that will have both ik and fk
                newJoint = joint.replace("BIND", "FK")

                cmds.joint(name=newJoint, radius=0.5)
                cmds.matchTransform(newJoint, joint)
                cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

            cmds.select(clear=True)

    # add controls to all joints except last one
    for extremity in jointList:
        for joint in extremity[:-1]:

            # create controls
            controlSuffix = "FK_CTRL" if limbType == "leg" else "CTRL"
            controlName = joint.replace("BIND_JNT", controlSuffix)
            control, group = createControl(name=controlName, shape="circle", size=(controlSize * 1.5))

            cmds.matchTransform(group, joint, scale=False)
            transferTransformsToOPM(group)

            # parent constraint to bind joint or fk joint depending on setup
            if limbType == "leg" and reverseFoot:
                cmds.parentConstraint(control, joint.replace("BIND", "FK"))
            else:
                cmds.parentConstraint(control, joint)

            # parent control to previous control
            prevJoint = cmds.listRelatives(joint, parent=True, type="joint")[0]
            prevControl = prevJoint.replace("BIND_JNT", controlSuffix)
            if cmds.objExists(prevControl):
                cmds.parent(group, prevControl)

            # HIERARCHY
            if joint == extremity[0]:
                if limbType == "arm":
                    cmds.parent(group, handControlGroup)
                else:
                    cmds.parent(group, footControlGroup)

    # parent base controls to hand bind joint
    for extremity in jointList:
        cmds.parentConstraint(jointChain[2], extremity[0].replace("BIND_JNT", controlSuffix), maintainOffset=True)

    cmds.select(clear=True)


def createFootIK(foot: str, toeList: list[list[str]], jointChain: list[str], reverseFootJoints: tuple[str]):
    """ Create the setup for IK foot. """

    # unpack reverse foot joints
    heelJoint, tipJoint, ballJoint, mainJoint = reverseFootJoints

    # create new joint chain
    for toe in toeList:
        for toeJoint in toe:
            newJoint = toeJoint.replace("BIND", "IK")

            cmds.joint(name=newJoint, radius=0.5)
            cmds.matchTransform(newJoint, toeJoint)
            cmds.makeIdentity(newJoint, apply=True, rotate=True, scale=False)

        cmds.select(clear=True)
    
    # create extra ik stabiliser joint and position it
    stabiliser = cmds.joint(name=f"{foot}stabiliser_IK_JNT", radius=1)
    cmds.select(clear=True)

    cmds.matchTransform(stabiliser, jointChain[2])
    cmds.setAttr(f"{stabiliser}.translateY", 0)
    cmds.parent(stabiliser, jointChain[2].replace("BIND", "IK"))

    # translateZ = cmds.getAttr(f"{toeList[0][0]}.translateZ")
    # cmds.setAttr(f"{stabiliser}.translateZ", translateZ)

    # parent joints to main skeletons
    for toe in toeList:
        cmds.parent(toe[0].replace("BIND", "FK"), jointChain[2].replace("BIND", "FK"))
        cmds.parent(toe[0].replace("BIND", "IK"), jointChain[2].replace("BIND", "IK"))


    # CREATE IK HANDLES

    # stabiliser handle
    ankleHandle = cmds.ikHandle(name=jointChain[2].replace("BIND_JNT", "HNDL"),
                                solver="ikSCsolver",
                                startJoint=jointChain[2].replace("BIND", "IK"),
                                endEffector=stabiliser)[0]
    cmds.parent(ankleHandle, heelJoint)

    # toe handles
    for toe in toeList:
        cmds.ikHandle(name=f"{toe[0]}_HNDL",
                        solver="ikSCsolver",
                        startJoint=toe[0].replace("BIND", "IK"),
                        endEffector=toe[1].replace("BIND", "IK"))
        
        cmds.ikHandle(name=f"{toe[1]}_HNDL",
                        solver="ikSCsolver",
                        startJoint=toe[1].replace("BIND", "IK"),
                        endEffector=toe[2].replace("BIND", "IK"))

        # create offset group and parent handle to it, then parent handle to reverse joints
        for i in range(2):
            cmds.group(empty=True, name=f"{toe[i]}_OFFSET")
            cmds.matchTransform(f"{toe[i]}_OFFSET", f"{toe[i]}_HNDL")
            cmds.parent(f"{toe[i]}_HNDL", f"{toe[i]}_OFFSET")

        cmds.parent(f"{toe[0]}_OFFSET", ballJoint)
        cmds.parent(f"{toe[1]}_OFFSET", tipJoint)

    # parent ik handle to reverse foot main joint
    cmds.parent(f"{limb}_HNDL", mainJoint)



def createFootIKFKswitch(toeList: list[list[str]]) -> str:
    """ Create the switch between FK and IK joints, then connect it to the a new foot IK/FK switch attribute.
    
    Return name of IKFK switch attribute. """

    # add IK/FK switch attribute
    cmds.select(IKFKswitch)
    cmds.addAttr(attributeType="float",
                    hasMaxValue=True, hasMinValue=True,
                    maxValue=1, minValue=0,
                    longName="footIKFKswitch",
                    niceName="Foot IK/FK Switch")
    cmds.setAttr(f"{IKFKswitch}.footIKFKswitch", keyable=True)
    cmds.setAttr(f"{IKFKswitch}.footIKFKswitch", 1)
    cmds.select(clear=True)

    # reverse node
    reverse = cmds.shadingNode("reverse", asUtility=True, name=f"{limb}_foot_IKFK_reverse")
    cmds.connectAttr(f"{IKFKswitch}.footIKFKswitch",
                     f"{reverse}.inputX",
                     force=True)

    # set up switch for foot
    for toe in toeList:
        for joint in toe:
            cmds.parentConstraint(joint.replace("BIND", "FK"),
                                  joint.replace("BIND", "IK"),
                                  joint,
                                  maintainOffset=False)

            getConstraint = cmds.listConnections(joint, type="parentConstraint")[0]
            getWeights = cmds.parentConstraint(getConstraint, query=True, weightAliasList=True)

            cmds.connectAttr(f"{IKFKswitch}.footIKFKswitch",
                             f"{getConstraint}.{getWeights[0]}",
                             force=True)
            cmds.connectAttr(f"{reverse}.outputX",
                             f"{getConstraint}.{getWeights[1]}",
                             force=True)

    return "footIKFKswitch"


def createFootRoll(foot: str, reverseFootJoints: tuple[str]) -> str:
    """ Setup foot roll using a new control.
     
    Return name of roll control. """

    # unpack reverse foot joints
    heelJoint, tipJoint, ballJoint, mainJoint = reverseFootJoints

    controlMultiplier = 10
    ballLimit = 3

    # CONTROL
    
    # create roll control
    rollControl, rollGroup = createControl(name=f"{foot}_roll_CTRL", shape="4arrows", size=(1 * controlSize))
    IKcontrols.append(rollControl)

    # fix control rotation
    cmds.rotate(0, 0, -90, rollControl)
    cmds.makeIdentity(rollControl, apply=True, scale=True, rotate=True)

    # move control into position
    cmds.matchTransform(rollGroup, f"{limb}_IK_CTRL")

    cmds.move(0, 0, (30 * globalScale), rollGroup,
            relative=True, objectSpace=True, worldSpaceDistance=True)

    # UNCOMMENT IF IK CONTROL IS INVERSED LIKE THE JOINT
    # if limbSide == "L":
    #     cmds.move(0, 0, (30 * globalScale), rollGroup,
    #             relative=True, objectSpace=True, worldSpaceDistance=True)
    # else:
    #     cmds.move(0, 0, (-30 * globalScale), rollGroup,
    #             relative=True, objectSpace=True, worldSpaceDistance=True)
        
    cmds.setAttr(f"{rollGroup}.translateY", 0)
    transferTransformsToOPM(rollGroup)
    cmds.parentConstraint(f"{limb}_IK_CTRL", rollGroup, maintainOffset=True)

    # parent control
    cmds.parent(rollGroup, footControlGroup)

    rollControlZ = f"{rollControl}.translateZ"

    # UNCOMMENT IF IK CONTROL IS INVERSED LIKE THE JOINT
    # set translate Z value to influence the roll, inverse for right side bc the joints are mirrored
    # if limbSide == "L":
    #     rollControlZ = f"{rollControl}.translateZ"
    # else:
    #     cmds.shadingNode("reverse", asUtility=True, name=f"{foot}_reverse")
    #     cmds.connectAttr(f"{rollControl}.translateZ", f"{foot}_reverse.inputX")
    #     rollControlZ = f"{foot}_reverse.outputX"

    # NODE SETUP

    # multiply divide
    multi = cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{foot}_roll_multi")
    cmds.setAttr(f"{multi}.input2X", controlMultiplier)
    cmds.connectAttr(rollControlZ, f"{multi}.input1X", force=True)
    
    # plus minus average
    pmaReverse = cmds.shadingNode("plusMinusAverage", asUtility=True, name=f"{foot}_roll_reverse_pma")
    pmaSubtract = cmds.shadingNode("plusMinusAverage", asUtility=True, name=f"{foot}_roll_subtract_pma")

    cmds.setAttr(f"{pmaReverse}.operation", 2)        # 2 = subtract
    cmds.setAttr(f"{pmaSubtract}.operation", 1)        # 1 = sum
    cmds.setAttr(f"{pmaReverse}.input1D[0]", ballLimit * controlMultiplier)
    cmds.setAttr(f"{pmaSubtract}.input1D[0]", ballLimit * controlMultiplier)

    cmds.connectAttr(f"{multi}.outputX", f"{pmaReverse}.input1D[1]", force=True)
    cmds.connectAttr(f"{pmaReverse}.output1D", f"{pmaSubtract}.input1D[1]", force=True)

    # tip multiply divide
    multiTip = cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{foot}_roll_tip_multi")
    cmds.setAttr(f"{multiTip}.input2X", -1)
    cmds.connectAttr(f"{pmaReverse}.output1D", f"{multiTip}.input1X", force=True)


    # clamp condition
    conditionClamp = cmds.shadingNode("condition", asUtility=True, name=f"{foot}_roll_clamp_condition")
    cmds.setAttr(f"{conditionClamp}.operation", 4)

    cmds.connectAttr(f"{multi}.outputX", f"{conditionClamp}.firstTerm", force=True)
    cmds.connectAttr(f"{multi}.outputX", f"{conditionClamp}.colorIfFalseR", force=True)

    # heel condition
    conditionHeel = cmds.shadingNode("condition", asUtility=True, name=f"{foot}_roll_heel_condition")
    cmds.setAttr(f"{conditionHeel}.operation", 4)
    cmds.setAttr(f"{conditionHeel}.colorIfFalseR", 0)

    cmds.connectAttr(f"{multi}.outputX", f"{conditionHeel}.firstTerm", force=True)
    cmds.connectAttr(f"{multi}.outputX", f"{conditionHeel}.colorIfTrueR", force=True)

    # main condition
    condition = cmds.shadingNode("condition", asUtility=True, name=f"{foot}_roll_condition")

    cmds.setAttr(f"{condition}.operation", 4)
    cmds.setAttr(f"{condition}.secondTerm", ballLimit)
    cmds.setAttr(f"{condition}.colorIfFalseR", ballLimit * controlMultiplier)

    cmds.connectAttr(rollControlZ, f"{condition}.firstTerm", force=True)

    cmds.connectAttr(f"{conditionClamp}.outColorR", f"{condition}.colorIfTrueR", force=True)
    cmds.connectAttr(f"{pmaSubtract}.output1D", f"{condition}.colorIfFalseR", force=True)
    cmds.connectAttr(f"{multiTip}.outputX", f"{condition}.colorIfFalseG", force=True)


    # connect to reverse foot joints
    cmds.connectAttr(f"{condition}.outColorR", f"{ballJoint}.rotateX", force=True)
    cmds.connectAttr(f"{condition}.outColorG", f"{tipJoint}.rotateX", force=True)
    cmds.connectAttr(f"{conditionHeel}.outColorR", f"{heelJoint}.rotateX", force=True)

    return rollControl



def createFootBank(foot: str, rollControl: str, reverseFootJoints: tuple[str]):
    """ Setup foot bank using a new control.
         
    Return name of roll control. """

    # unpack reverse foot joints
    heelJoint, tipJoint, ballJoint, mainJoint = reverseFootJoints

    outerGroup = cmds.group(empty=True, name=f"{foot}_outer_OFFSET")
    innerGroup = cmds.group(empty=True, name=f"{foot}_inner_OFFSET")
    mainGroup = cmds.group(empty=True, name=f"{foot}_OFFSET")

    for group in [outerGroup, innerGroup]:
        if group == outerGroup:
            offset = 4
        else:
            offset = -4

        cmds.matchTransform(group, f"{limb}_IK_CTRL")
        cmds.move(offset, 0, 0, group,
                  relative=True, objectSpace=True, worldSpaceDistance=True)
        cmds.setAttr(f"{group}.translateY", 0)

    cmds.parent(innerGroup, outerGroup)
    cmds.parent(outerGroup, mainGroup)
    cmds.parent(mainGroup, IKFKgroup)
    cmds.parentConstraint(f"{limb}_IK_CTRL", mainGroup, maintainOffset=True)

    # parent reverse foot joints to group
    cmds.parent(heelJoint, innerGroup)


    # NODES
    multi = cmds.shadingNode("multiplyDivide", asUtility=True, name=f"{foot}_bank_multi")
    cmds.connectAttr(f"{rollControl}.translateX", f"{multi}.input1X", force=True)
    cmds.setAttr(f"{multi}.input2X", -5)

    condition = cmds.shadingNode("condition", asUtility=True, name=f"{foot}_bank_condition")
    cmds.setAttr(f"{condition}.operation", 2)       # 2 = greater than
    cmds.setAttr(f"{condition}.colorIfFalseR", 0)

    cmds.connectAttr(f"{rollControl}.translateX", f"{condition}.firstTerm", force=True)
    cmds.connectAttr(f"{multi}.outputX", f"{condition}.colorIfTrueR", force=True)
    cmds.connectAttr(f"{multi}.outputX", f"{condition}.colorIfFalseG", force=True)

    cmds.connectAttr(f"{condition}.outColorR", f"{outerGroup}.rotateZ", force=True)
    cmds.connectAttr(f"{condition}.outColorG", f"{innerGroup}.rotateZ", force=True)



def _______________BUILD_______________(): pass


def buildLimbRig(globalScaleField: str,
                 controlSizeField: str,
                 limbStretchBox: str,
                 handBox: str = "",
                 clavicleBox: str = "",
                 footBox: str = "",
                 revFootBox: str = ""):
    """ Rig the limb. """

    global globalScale
    global controlSize
    global limbStretch

    global rigHand
    global clavicleControl

    global rigFoot
    global reverseFoot

    global rootJoint
    global limbSide
    global limb

    # BUILD NAMES
    
    globalScale = cmds.floatField(globalScaleField, query=True, value=True)
    controlSize = cmds.floatField(controlSizeField, query=True, value=True) * globalScale
    limbStretch = cmds.checkBox(limbStretchBox, query=True, value=True)

    limbSide = cmds.ls(selection=True, type="joint")[0][0]

    if limbType == "arm":
        rigHand = cmds.checkBox(handBox, query=True, value=True)
        clavicleControl = cmds.checkBox(clavicleBox, query=True, value=True)

    if limbType == "leg":
        rigFoot = cmds.checkBox(footBox, query=True, value=True)
        reverseFoot = cmds.checkBox(revFootBox, query=True, value=True)

    limb = f"{limbSide}_{limbType}"

    # create list of joint hierarchy (including selected joint)
    rootJoint = cmds.ls(selection=True, type="joint")[0]
    midJoint = cmds.listRelatives(rootJoint, type="joint")[0]
    endJoint = cmds.listRelatives(midJoint, type="joint")[0]

    jointChain = [rootJoint, midJoint, endJoint]

    # reverse foot names
    foot = f"{limbSide}_foot"

    heelJoint = f"{foot}_heel_REV_JNT"
    tipJoint = f"{foot}_tip_REV_JNT"
    ballJoint = f"{foot}_ball_REV_JNT"
    mainJoint = f"{foot}_REV_JNT"

    reverseFootJoints = (heelJoint, tipJoint, ballJoint, mainJoint)

    # BUILD LIMB RIG
    createHierarchy()
    createLimbFK(jointChain=jointChain)
    createLimbIK(jointChain=jointChain)

    attributes = createLimbIKFKswitch(jointChain=jointChain)

    if limbStretch:
        stretchAttributes = createStretch(limb=limb, jointChain=jointChain)
        attributes.append(stretchAttributes[0])
        attributes.append(stretchAttributes[1])

    setDrawingOverrides(limbControlGroup)


    # CREATE HAND RIG
    if limbType == "arm" and rigHand:
        fingerList = getFingers()
        createExtremityFK(jointList=fingerList, jointChain=jointChain)
        setDrawingOverrides(handControlGroup)

        if clavicleControl:
            createClavicle(jointChain=jointChain)


    # CREATE FOOT RIG
    if limbType == "leg" and rigFoot:
        toeList = getToes()
        createExtremityFK(jointList=toeList, jointChain=jointChain)
    
        if reverseFoot:
            createFootIK(foot=foot, toeList=toeList, jointChain=jointChain, reverseFootJoints=reverseFootJoints)
            footIKFKattribute = createFootIKFKswitch(toeList=toeList)
            attributes.append(footIKFKattribute)
            rollControl = createFootRoll(foot=foot, reverseFootJoints=reverseFootJoints)
            createFootBank(foot=foot, rollControl=rollControl, reverseFootJoints=reverseFootJoints)

            if limbStretch:
                cmds.parent(f"{limb}_endPos_LOC", f"{foot}_REV_JNT")

        setDrawingOverrides(footControlGroup)

    setDrawingOverrides(rigGroup, colour="pink")

    createProxyAttributes(attributes=attributes)
    createIKFKvisibility()



def buildArmRig(globalScaleField: str,
                controlSizeField: str,
                limbStretchBox: str,
                handBox: str,
                clavicleBox: str,
                *args):

    global limbType
    limbType = "arm"
    
    buildLimbRig(globalScaleField=globalScaleField,
                 controlSizeField=controlSizeField,
                 limbStretchBox=limbStretchBox,
                 handBox=handBox,
                 clavicleBox=clavicleBox)



def buildLegRig(globalScaleField: str,
                controlSizeField: str,
                limbStretchBox: str,
                footBox: str,
                revFootBox: str,
                *args):
    
    global limbType
    limbType = "leg"
    
    buildLimbRig(globalScaleField=globalScaleField,
                 controlSizeField=controlSizeField,
                 limbStretchBox=limbStretchBox,
                 footBox=footBox,
                 revFootBox=revFootBox)


createUI(buildArmRig, buildLegRig)