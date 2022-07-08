/* eslint-disable prettier/prettier */
import React from 'react';

import {View, Image, Text, StyleSheet} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';

const ImageUploader = ({handleGalleryPhoto, handleCameraPhoto, photo}) => {
  return (
    <View style={styles.imageView}>
      {photo && <Image source={{uri: photo.uri}} style={styles.photo} />}
      <View style={styles.buttonContainer}>
        <Icon.Button size={30} name="camera" color="#a5d3f2" backgroundColor="gray" onPress={handleCameraPhoto}>
          <Text style={styles.buttonText}>Camera</Text>
        </Icon.Button>

        <Icon.Button size={30} name="photo" color="#a5d3f2" backgroundColor="gray" onPress={handleGalleryPhoto}>
          <Text style={styles.buttonText}>Gallery</Text>
        </Icon.Button>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  imageView: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: 15,
  },
  photo: {
    borderWidth: 2,
    borderColor: 'gray',
    top: 60,
    width: 200,
    height: 280,
  },
  buttonContainer: {
    right: 30,
    left: 30,
    position: 'absolute',
    top: 5,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  buttonText: {
    color: 'white',
  },
});

export default ImageUploader;
