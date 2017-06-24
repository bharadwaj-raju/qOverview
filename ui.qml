import QtQuick 2.7
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0

Item {
	id: "root"
	objectName: "root"

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

		color: Qt.rgba(overlaycolor[0], overlaycolor[1], overlaycolor[2], overlaycolor[3])
	}

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
			//bottomMargin: 810
			//leftMargin: 550
			//rightMargin: 545
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
				//horizontalCenter: parent.horizontalCenter
			}

			Repeater {
				id: "dockloop"
				objectName: "dockloop"

				model: Python.get_dock_items()

				Image {
					source: modelData[2]

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


	Flickable {

		id: "windowsscrollview"
		objectName: "windowsscrollview"

		//contentHeight: windowsgrid.height

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

			//property int rowCount: parent.width / (elements.itemAt(0).width + spacing)
			//property int rowWidth: rowCount * elements.itemAt(0).width + (rowCount - 1) * spacing
			//property int mar: (parent.width - rowWidth) / 2

			anchors {
				fill: parent
				//leftMargin: mar
				//rightMargin: mar
				horizontalCenter: parent.horizontalCenter
				verticalCenter: parent.verticalCenter
			}

			Repeater {
				id: "windowsloop"
				model: Python.get_windows()

				Image {
					source: modelData[1]
					height: (sourceSize.height / 10) * 2
					width: (sourceSize.width / 10) * 2

					MouseArea {
						anchors.fill: parent
						acceptedButtons: Qt.LeftButton | Qt.MiddleButton
						onPressed: {
							if (pressedButtons & Qt.LeftButton) {
								Python.window_clicked(modelData[2])
							}

							else {
								if (pressedButtons & Qt.MiddleButton) {
									if (Python.is_midbutton_enabled()) {
										Python.window_clicked_midbutton(modelData[2])
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
						width: parent.width + 2

						anchors {
							bottom: parent.bottom
							horizontalCenter: parent.horizontalCenter
							//verticalCenter: parent.verticalCenter
						}

						Text {
							id: "windowoverlaytext"
							text: modelData[0]
							color: "#fff"
							width: parent.width - 2
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

	Flow {
		visible: false

		id: "appsgrid"
		objectName: "appsgrid"

		spacing: 20

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

				Image {
					source: modelData[2]
					height: 48
					width: 48

					MouseArea {
						anchors.fill: parent
						hoverEnabled: true
						onClicked: {
							Python.app_clicked(modelData[1])
						}
						onEntered: {
							applabel.visible = true
						}
						onExited: {
							applabel.visible = false
						}
					}


					Rectangle {
						id: "applabel"
						color: "#3A4055"

						visible: false

						height: applabeltext.paintedHeight + 2
						width: applabeltext.paintedWidth + 2

						anchors {
							top: parent.bottom
							//horizontalCenter: parent.horizontalCenter
						}

						Text {
							id: "applabeltext"
							text: modelData[0]
							color: "#fff"
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

