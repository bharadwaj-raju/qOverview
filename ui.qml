import QtQuick 2.7
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0

#ifdef KDEPLASMA
import org.kde.plasma.core 2.0
#endif

Item {
	id: "root"
	objectName: "root"

	/* BACKGROUND IMAGE */

	Image {
		id: "backgroundimg"
		objectName: "backgroundimg"
		source: Python.get_background()

		anchors.fill: parent

		visible: false

		MouseArea {
			anchors.fill: parent

			onClicked: {
				searchfield.focus = false; windowsgrid.visible = true
			}
		}

	}

	ColorOverlay {
		id: "background"
		objectName: "background"

		anchors.fill: backgroundimg
		source: backgroundimg

		property var overlaycolor: Python.get_background_overlay_color()

		MouseArea {
			anchors.fill: parent

			onClicked: {
				Python.background_clicked()
			}
		}


		color: Qt.rgba(overlaycolor[0], overlaycolor[1], overlaycolor[2], overlaycolor[3])
	}

	/* SEARCH BAR */

	TextField {
		id: "searchfield"
		objectName: "searchfield"
		placeholderText: "Search applications…"

		focus: true

		width: 500
		height: 30

		anchors {
			top: root.top
			topMargin: 50
			horizontalCenter: parent.horizontalCenter
		}

		style: TextFieldStyle {
			background: Rectangle {
				color: "#3A4055"
				radius: 50
			}
			textColor: "white"
			placeholderTextColor: "white"
		}

		MouseArea {
			anchors.fill: parent
			propagateComposedEvents: true

			onClicked: {
				windowsgrid.visible = false
				searchfield.focus = true
			}
		}

		Keys.onReleased: {
			if (searchfield.length == 0) {
				windowsgrid.visible = true
				appsgrid.visible = false
			}

			else {
				appsloop.model = Python.search(searchfield.text)
				windowsgrid.visible = false
				appsgrid.visible = true
			}
		}

	}

	/* DOCK */

	Rectangle {
		id: "dockrect"
		objectName: "dockrect"

		color: "#3A4055"

		property int dockHeight: dock.height + 20

		width: 80
		height: dockHeight

		anchors {
			left: root.left
			verticalCenter: parent.verticalCenter
		}

		Component.onCompleted: {
			if (! Python.is_dock_enabled()) {
				visible = false
			}
		}

		Column {
			id: "dock"
			objectName: "dock"

			spacing: 10
			leftPadding: 10

			anchors {
				leftMargin: 10
				verticalCenter: parent.verticalCenter
			}

			Repeater {
				id: "dockloop"
				objectName: "dockloop"

				model: Python.get_dock_items()

				#ifdef KDEPLASMA
				IconItem {
					source: modelData[2]
					width: units.iconSizes.huge
					height: units.iconSizes.huge
				#else
				Image {
					source: modelData[2]
				#endif

					MouseArea {
						anchors.fill: parent
						onClicked: {
							Python.app_clicked(modelData[1])
						}
					}
				}
			}


		}

	}

	/* WORKSPACES */

	Rectangle {
		id: "workspacerect"
		objectName: "workspacerect"

		color: "#3A4055"

		property int workspaceHeight: workspaces.height + 20

		width: 80
		height: workspaceHeight

		anchors {
			right: root.right
			verticalCenter: parent.verticalCenter
		}


		Column {
			id: "workspaces"
			objectName: "workspaces"

			spacing: 10
			leftPadding: 10

			anchors {
				leftMargin: 10
				verticalCenter: parent.verticalCenter
				//horizontalCenter: parent.horizontalCenter
			}

			Repeater {
				id: "workspaceloop"
				objectName: "workspaceloop"

				model: Python.get_workspaces()

				Rectangle {

					width: 64
					height: 64

					Text {
						text: modelData

						anchors {
							horizontalCenter: parent.horizontalCenter
							verticalCenter: parent.verticalCenter
						}

						Component.onCompleted: {
							if (Python.get_current_workspace() == modelData) {
								parent.color = "lightblue"
							}

							if (! Python.is_workspaces_enabled()) {
								workspacerect.visible = false
							}

						}

					}

					MouseArea {
						anchors.fill: parent
						onClicked: {
							Python.workspace_clicked(modelData)
						}
					}
				}
			}

		}

	}

	/* WINDOWS */


	Flickable {

		id: "windowsscrollview"
		objectName: "windowsscrollview"

		anchors {
			fill: parent
			leftMargin: 270
			rightMargin: 250
			topMargin: 280
			bottomMargin: 100
			horizontalCenter: parent.horizontalCenter
			verticalCenter: parent.verticalCenter
		}


		Flow {
			id: "windowsgrid"
			objectName: "windowsgrid"

			spacing: 20

			anchors {
				fill: parent
				horizontalCenter: parent.horizontalCenter
				verticalCenter: parent.verticalCenter
			}

			Repeater {
				id: "windowsloop"
				model: Python.get_windows(Python.get_current_workspace())

				#ifdef KDEPLASMA
				WindowThumbnail {
					winId: modelData[2]
					width: 288
					height: 140
				#else
				Image {
					source: modelData[2]
					width: (sourceSize.width / 10) * 2
					height: (sourceSize.height / 10) * 2
				#endif

					MouseArea {
						anchors.fill: parent
						acceptedButtons: Qt.LeftButton | Qt.MiddleButton
						onPressed: {
							if (pressedButtons & Qt.LeftButton) {
								Python.window_clicked(modelData[1])
							}

							else {
								if (pressedButtons & Qt.MiddleButton) {
									if (Python.is_midbutton_enabled()) {
										Python.window_clicked_midbutton(modelData[1])
										parent.visible = false
									}
								}
							}
						}

					}

					Rectangle {
						id: "windowoverlay"
						color: "#3A4055"

						height: windowoverlaytext.paintedHeight + 2
						width: 288 + 2

						anchors {
							bottom: parent.bottom
							horizontalCenter: parent.horizontalCenter
							//verticalCenter: parent.verticalCenter
						}

						Text {
							id: "windowoverlaytext"
							text: modelData[0]
							color: "#fff"
							width: 288
							elide: Text.ElideMiddle

							horizontalAlignment: Text.AlignHCenter

							anchors {
								horizontalCenter: parent.horizontalCenter
								verticalCenter: parent.verticalCenter
							}

						}
					}


				}

			}
		}
	}

	/* APPS */

	Flow {
		visible: false

		id: "appsgrid"
		objectName: "appsgrid"

		spacing: 50

		anchors {
			fill: parent
            leftMargin: 270
			rightMargin: 250
			topMargin: 280
			bottomMargin: 100
			horizontalCenter: parent.horizontalCenter
			verticalCenter: parent.verticalCenter
		}

		Repeater {
			id: "appsloop"
			objectName: "appsloop"

			model: [['Name', 'EntryName', 'IconPath']]

				#ifdef KDEPLASMA
				IconItem {
					source: modelData[2]
					height: units.iconSizes.huge
					width: units.iconSizes.huge
				#else
				Image {
					source: modelData[2]
				#endif

					MouseArea {
						anchors.fill: parent
						onClicked: {
							Python.app_clicked(modelData[1])
						}
					}


					Rectangle {
						id: "applabel"
						color: "transparent"

						height: applabeltext.paintedHeight + 2
						width: parent.paintedWidth + 20

						anchors {
							top: parent.bottom
							horizontalCenter: parent.horizontalCenter
						}

						Text {
							id: "applabeltext"
							text: modelData[0]
							color: "#fff"

							width: parent.width
							wrapMode: Text.WordWrap

							horizontalAlignment: Text.AlignHCenter

							anchors {
								horizontalCenter: parent.horizontalCenter
								verticalCenter: parent.verticalCenter
							}

						}


					}
				}

		}

	}

}

