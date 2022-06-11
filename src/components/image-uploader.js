/* eslint-disable prettier/prettier */
import React from 'react';
import {View, Image, Button, StyleSheet} from 'react-native';

const ImageUploader = ({handleGalleryPhoto, handleCameraPhoto, photo}) => {
  return (
    <View style={styles.imageView}>
      {photo && <Image source={{uri: photo.uri}} style={styles.photo} />}
      <Button
        style={styles.photoBtn}
        title="Choose Gallery Picture"
        onPress={handleGalleryPhoto}
      />
      <Button
        style={styles.photoBtn}
        title="Take Picture"
        onPress={handleCameraPhoto}
      />
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
    width: 200,
    height: 200,
  },
});

export default ImageUploader;
